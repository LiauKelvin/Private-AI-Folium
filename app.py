import gradio as gr
import ollama
import os
import time
import json
import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# --- Setup & Constants ---
DB_DIR = "./folium_db"
HISTORY_FILE = "chat_history.json"

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

def extract_text(content):
    if isinstance(content, str): return content
    elif isinstance(content, list): return " ".join([item.get("text", "") for item in content if isinstance(item, dict) and "text" in item])
    elif isinstance(content, dict): return content.get("text", "")
    return str(content)

# --- Logic: File Management ---
def get_installed_models():
    try:
        response = ollama.list()
        all_models = [getattr(m, 'model', getattr(m, 'name', '')) for m in response.models]
        chat_models = [m for m in all_models if "nomic" not in m.lower() and "embed" not in m.lower()]
        return chat_models
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return ["qwen2.5:1.5b"]

def upload_file(files):
    if not files: return "No files uploaded."
    status = ""
    for f in files:
        loader = PyPDFLoader(f.name)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        vector_db.add_documents(splitter.split_documents(docs))
        status += f"Berhasil: {os.path.basename(f.name)}\n"
    return status

def get_db_status():
    try:
        return f"Total potongan dokumen: {vector_db._collection.count()}"
    except:
        return "Database kosong."

def clear_db():
    global vector_db
    vector_db.delete_collection()
    vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return "Database dibersihkan."

# --- Logic: Chat History Management ---
def get_saved_chats():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f:
        return list(json.load(f).keys())

def save_chat(history):
    if not history: return gr.update()
    data = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f: data = json.load(f)
    first_msg_content = extract_text(history[0]["content"])
    short_msg = first_msg_content[:15] + "..." if len(first_msg_content) > 15 else first_msg_content
    chat_name = f"{datetime.datetime.now().strftime('%d/%m %H:%M')} | {short_msg}"
    data[chat_name] = history
    with open(HISTORY_FILE, "w") as f: json.dump(data, f)
    return gr.update(choices=list(data.keys()), value=chat_name)

def load_chat(chat_name):
    if not chat_name or not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f: data = json.load(f)
    return data.get(chat_name, [])

def delete_saved_chat(chat_name):
    if not chat_name or not os.path.exists(HISTORY_FILE): return gr.update(), []
    with open(HISTORY_FILE, "r") as f: data = json.load(f)
    if chat_name in data:
        del data[chat_name]
        with open(HISTORY_FILE, "w") as f: json.dump(data, f)
    return gr.update(choices=list(data.keys()), value=None), []

def clear_current_chat():
    return []

def rename_saved_chat(old_name, new_name):
    if not old_name or not new_name or not os.path.exists(HISTORY_FILE):
        return gr.update(), gr.update()
    
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)
        
    if old_name in data and new_name not in data:
        data[new_name] = data.pop(old_name)
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f)
            
    new_choices = list(data.keys())
    return gr.update(choices=new_choices, value=new_name), gr.update(value="")

# --- Core Chat Engine ---
def user_sends_message(user_message, history):
    if history is None: history = []
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": ""})
    return "", history

def ai_responds(history, mode, system_prompt, model_name):
    start_time = time.time()
    if not history: return history
    
    user_message = extract_text(history[-2]["content"])
    sys_msg = system_prompt
    sources_text = ""
    ollama_messages = []
    current_temp = 0.7 

    # Mode Summarize
    if mode == "Summarize":
        try:
            db_data = vector_db.get(limit=15)
            if not db_data['documents']:
                history[-1]["content"] = "❌ Database kosong. Silakan upload PDF."
                yield history
                return
            context = "\n---\n".join(db_data['documents'])
            ollama_messages = [
                {'role': 'system', 'content': 'Anda adalah ahli perangkum. Buatlah ringkasan dari dokumen berikut HANYA dalam 3-5 poin-poin utama yang singkat, padat, dan jelas. Hindari kalimat bertele-tele.'},
                {'role': 'user', 'content': f"Rangkum materi ini:\n{context}"}
            ]
            current_temp = 0.3 
        except Exception as e:
            history[-1]["content"] = f"❌ Error: {str(e)}"
            yield history
            return

    else:
        # Mode RAG
        if mode == "RAG":
            try:
                results = vector_db.similarity_search(user_message, k=8)
                context_chunks = []
                for i, doc in enumerate(results):
                    context_chunks.append(doc.page_content)
                    source_name = os.path.basename(doc.metadata.get('source', 'Unknown'))
                    sources_text += f"\n* Sumber {i+1}: {source_name} (Hal {doc.metadata.get('page', 0)})"
                
                if not context_chunks:
                    history[-1]["content"] = "❌ Anda belum mengupload dokumen. Silakan upload PDF!"
                    yield history
                    return

                sys_msg = (
                    "Anda adalah asisten AI yang sangat teliti. Anda HANYA boleh menjawab "
                    "berdasarkan teks di dalam [KONTEKS DOKUMEN] di bawah ini. "
                    "DILARANG KERAS menggunakan pengetahuan Anda sendiri di luar dokumen. "
                    "Jawablah dengan LENGKAP, DETAIL, dan MENYELURUH sesuai dengan informasi yang ada di dokumen. "
                    "Jika pertanyaan pengguna tidak ada hubungannya atau tidak ditemukan "
                    "jawabannya di dalam [KONTEKS DOKUMEN], Anda WAJIB menjawab dengan: "
                    "'Maaf, informasi tersebut tidak ditemukan di dalam dokumen.'\n\n"
                    "[KONTEKS DOKUMEN]:\n"
                ) + "\n---\n".join(context_chunks)
                current_temp = 0.0 

            except Exception as e:
                history[-1]["content"] = "❌ Database kosong. Silakan upload PDF terlebih dahulu."
                yield history
                return

        # Mode Basic
        elif mode == "Basic":
            sys_msg = system_prompt + "\n\nInstruksi Tambahan: Jawablah dengan ringkas dan langsung ke intinya. Hindari penjelasan panjang lebar kecuali diminta."
            current_temp = 0.7

        ollama_messages.append({'role': 'system', 'content': sys_msg})
        
        for msg in history[:-2]:
            if msg["role"] == "user":
                ollama_messages.append({'role': 'user', 'content': extract_text(msg["content"])})
            elif msg["role"] == "assistant" and msg["content"]:
                clean_a = extract_text(msg["content"]).split("<hr>")[0]
                ollama_messages.append({'role': 'assistant', 'content': clean_a})
                
        ollama_messages.append({'role': 'user', 'content': user_message})

    response = ollama.chat(
        model=model_name, 
        messages=ollama_messages, 
        stream=True,
        options={"temperature": current_temp}
    )
    
    partial_msg = ""
    for chunk in response:
        partial_msg += chunk['message']['content']
        history[-1]["content"] = partial_msg 
        yield history 
        
    if mode == "RAG" and sources_text:
        partial_msg += f"\n\n<hr>**Referensi:**{sources_text}"
    elapsed = round(time.time() - start_time, 2)
    partial_msg += f"\n\n<hr>⏱️ *Waktu: {elapsed} detik*"
    
    history[-1]["content"] = partial_msg
    yield history

# --- UI Layout ---

# FIX: Added .no-wrap-row to forcefully stop horizontal wrapping
custom_css = """
.gradio-container { max-width: 98% !important; width: 100% !important; }
.logo { display:flex; background-color: #FCC6BB; height: 70px; border-radius: 8px; justify-content: center; align-items: center; margin-bottom: 10px; }
footer { display: none !important; }
.refresh-btn { margin-top: 15px !important; }
.no-wrap-row { flex-wrap: nowrap !important; }
"""

with gr.Blocks(title="Folium AI", theme=gr.themes.Soft(primary_hue="red"), css=custom_css) as demo:
    gr.HTML("<div class='logo'><h1 style='color:#9C2007; font-weight: 900; font-size: 1.8em; margin:0;'>🍁 FOLIUM AI</h1></div>")
    
    with gr.Row():
        with gr.Column(scale=3, min_width=250):
            mode = gr.Radio(["RAG", "Basic", "Summarize"], label="Mode", value="Basic")
            
            with gr.Row(equal_height=False, elem_classes=["no-wrap-row"]):
                model_dropdown = gr.Dropdown(choices=get_installed_models(), value="qwen2.5:1.5b", label="AI Model", scale=4, min_width=120)
                refresh_model_btn = gr.Button("🔁 Refresh", scale=1, min_width=50, elem_classes=["refresh-btn"])
            
            with gr.Accordion("📜 Riwayat Percakapan", open=False):
                chat_dropdown = gr.Dropdown(choices=get_saved_chats(), label="Pilih Riwayat Percakapan")
                rename_input = gr.Textbox(show_label=False, placeholder="Ubah Nama & 'enter..'")
                with gr.Row():
                    load_btn = gr.Button("Buka", size="sm")
                    del_chat_btn = gr.Button("Hapus", variant="stop", size="sm")
            
            with gr.Accordion("🛠️ Pengaturan Prompt", open=False):
                system_prompt_input = gr.Textbox(value="Anda adalah asisten akademik yang ahli.", label="System Prompt", lines=2)
            
            with gr.Accordion("🗃️ Dokumen Pribadi", open=False):
                upload_button = gr.File(label="Upload PDF", file_count="multiple", file_types=[".pdf"])
                db_status = gr.Textbox(value=get_db_status(), label="Status DB", interactive=False)
                delete_db_btn = gr.Button("🗑️🚮 Kosongkan Database", variant="stop")
                
                upload_button.upload(upload_file, inputs=[upload_button], outputs=[db_status]).then(get_db_status, outputs=[db_status])
                delete_db_btn.click(clear_db, outputs=[db_status])

        with gr.Column(scale=7, min_width=300):
            chatbot = gr.Chatbot(height=500, label="Pusat Belajar")
            
            with gr.Row():
                msg_input = gr.Textbox(show_label=False, placeholder="Ketik pertanyaan di sini...", scale=8)
                submit_btn = gr.Button("Kirim ⌯⌲", scale=1, variant="primary")
            
            with gr.Row():
                new_chat_btn = gr.Button("💭 Chat Baru")
                save_chat_btn = gr.Button("📥 Simpan Chat Ini")

            # --- Events ---
            refresh_model_btn.click(fn=lambda: gr.Dropdown(choices=get_installed_models()), outputs=[model_dropdown])
            
            rename_input.submit(rename_saved_chat, inputs=[chat_dropdown, rename_input], outputs=[chat_dropdown, rename_input])
            
            submit_event = msg_input.submit(user_sends_message, [msg_input, chatbot], [msg_input, chatbot], queue=False).then(
                ai_responds, [chatbot, mode, system_prompt_input, model_dropdown], chatbot
            )
            submit_btn.click(user_sends_message, [msg_input, chatbot], [msg_input, chatbot], queue=False).then(
                ai_responds, [chatbot, mode, system_prompt_input, model_dropdown], chatbot
            )
            
            new_chat_btn.click(clear_current_chat, outputs=[chatbot])
            save_chat_btn.click(save_chat, inputs=[chatbot], outputs=[chat_dropdown])
            load_btn.click(load_chat, inputs=[chat_dropdown], outputs=[chatbot])
            del_chat_btn.click(delete_saved_chat, inputs=[chat_dropdown], outputs=[chat_dropdown, chatbot])

if __name__ == "__main__":
    import sys
    import os
    if sys.stdout is None: sys.stdout = open(os.devnull, "w")
    if sys.stderr is None: sys.stderr = open(os.devnull, "w")
    demo.launch(inbrowser=True, quiet=True)