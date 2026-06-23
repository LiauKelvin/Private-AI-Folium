import gradio as gr
import ollama
import os
import time
import json
import datetime
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
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

def get_directory_size(directory):
    total_size = 0
    if not os.path.exists(directory):
        return 0
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

# --- Logic: File Management ---
def get_installed_models():
    try:
        response = ollama.list()
        all_models = [getattr(m, 'model', getattr(m, 'name', '')) for m in response.models]
        chat_models = [m for m in all_models if "nomic" not in m.lower() and "embed" not in m.lower()]
        return chat_models if chat_models else ["qwen2.5:1.5b"]
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return ["qwen2.5:1.5b"]

def upload_file(files):
    if not files: return "No files uploaded."
    status = ""
    for f in files:
        ext = os.path.splitext(f.name)[1].lower()
        try:
            if ext == ".pdf":
                loader = PyPDFLoader(f.name)
            elif ext in [".docx", ".doc"]:
                loader = Docx2txtLoader(f.name)
            elif ext in [".pptx", ".ppt"]:
                loader = UnstructuredPowerPointLoader(f.name)
            else:
                status += f"Format tidak didukung: {os.path.basename(f.name)}\n"
                continue

            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            vector_db.add_documents(splitter.split_documents(docs))
            status += f"Berhasil: {os.path.basename(f.name)}\n"
        except Exception as e:
            status += f"Gagal {os.path.basename(f.name)}: {str(e)}\n"
            
    return status

def get_db_status():
    try:
        count = vector_db._collection.count()
        size_bytes = get_directory_size(DB_DIR)
        size_formatted = format_size(size_bytes)
        return f"Total potongan dokumen: {count}  |  Beban DB: {size_formatted}"
    except:
        return "Database kosong atau belum siap."

def clear_db():
    global vector_db
    vector_db.delete_collection()
    vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return "Database dibersihkan."

# --- Logic: Chat History Management ---
def get_saved_chats():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return list(json.load(f).keys())
    except json.JSONDecodeError:
        return []

def save_chat(history):
    if not history: return gr.update(), ""
    data = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f: data = json.load(f)
        except json.JSONDecodeError:
            pass
            
    first_msg_content = extract_text(history[0]["content"])
    short_msg = first_msg_content[:15] + "..." if len(first_msg_content) > 15 else first_msg_content
    chat_name = f"{datetime.datetime.now().strftime('%d/%m %H:%M')} | {short_msg}"
    
    data[chat_name] = history
    with open(HISTORY_FILE, "w") as f: json.dump(data, f)
    
    return gr.update(choices=list(data.keys()), value=chat_name), chat_name

def load_chat(chat_name):
    if not chat_name or not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f: data = json.load(f)
    return data.get(chat_name, [])

def delete_saved_chat(chat_name):
    if not chat_name or not os.path.exists(HISTORY_FILE): return gr.update(), [], ""
    with open(HISTORY_FILE, "r") as f: data = json.load(f)
    if chat_name in data:
        del data[chat_name]
        with open(HISTORY_FILE, "w") as f: json.dump(data, f)
    return gr.update(choices=list(data.keys()), value=None), [], ""

def clear_current_chat():
    return [], ""

def direct_rename_chat(new_name, old_name):
    if not old_name or not new_name or new_name == old_name:
        return gr.update(), old_name
        
    saved_chats = get_saved_chats()
    
    if new_name in saved_chats:
        return gr.update(value=new_name), new_name
        
    if old_name in saved_chats and new_name not in saved_chats:
        with open(HISTORY_FILE, "r") as f: data = json.load(f)
        data[new_name] = data.pop(old_name)
        with open(HISTORY_FILE, "w") as f: json.dump(data, f)
        return gr.update(choices=list(data.keys()), value=new_name), new_name
        
    return gr.update(value=old_name), old_name

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

    if mode == "Summarize":
        try:
            db_data = vector_db.get(limit=15)
            if not db_data.get('documents'):
                history[-1]["content"] = "❌ Database kosong. Silakan upload dokumen terlebih dahulu."
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
        if mode == "RAG":
            try:
                results = vector_db.similarity_search(user_message, k=8)
                context_chunks = []
                for i, doc in enumerate(results):
                    context_chunks.append(doc.page_content)
                    source_name = os.path.basename(doc.metadata.get('source', 'Unknown'))
                    sources_text += f"\n* Sumber {i+1}: {source_name} (Hal {doc.metadata.get('page', 0)})"
                
                if not context_chunks:
                    history[-1]["content"] = "❌ Anda belum mengupload dokumen. Silakan upload dokumen terlebih dahulu!"
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
                history[-1]["content"] = "❌ Database kosong. Silakan upload dokumen terlebih dahulu."
                yield history
                return

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

    try:
        response = ollama.chat(
            model=model_name, 
            messages=ollama_messages, 
            stream=True,
            options={
                "temperature": current_temp,
                "repeat_penalty": 1.15,
                "num_predict": 800
            }
        )
        
        partial_msg = ""
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                partial_msg += chunk['message']['content']
                history[-1]["content"] = partial_msg 
                yield history 
        
        if not partial_msg.strip():
            partial_msg = "⚠️ Model AI tidak mengembalikan data jawaban. Model mungkin tidak memiliki pengetahuan dasar atau kehabisan memori untuk memproses instruksi ini."
            
    except Exception as e:
        partial_msg = f"❌ Terjadi gangguan pada AI Model atau koneksi terputus: {str(e)}. Mohon pastikan Ollama berjalan atau coba ganti model lain."
        history[-1]["content"] = partial_msg
        yield history
        return
        
    if mode == "RAG" and sources_text:
        partial_msg += f"\n\n<hr>**Referensi:**{sources_text}"
    elapsed = round(time.time() - start_time, 2)
    partial_msg += f"\n\n<hr>⏱️ *Waktu: {elapsed} detik*"
    
    history[-1]["content"] = partial_msg
    yield history

# --- UI Layout & CSS ---
custom_css = """
body { background-color: #f1f5f9 !important; }
.gradio-container { max-width: 98% !important; width: 100% !important; }

.logo { 
    display:flex; 
    background-color: #e6fced; 
    height: 70px; 
    border-radius: 12px; 
    justify-content: center; 
    align-items: center; 
    margin-bottom: 20px; 
    border: none !important; 
    box-shadow: 0 8px 20px rgba(0,0,0,0.06) !important; 
}

footer { display: none !important; }
.refresh-btn { margin-top: 28px !important; }
.no-wrap-row { flex-wrap: nowrap !important; }

.custom-panel {
    background-color: #ffffff !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12) !important;
}

.custom-accordion {
    border: none !important;
    border-radius: 12px !important;
    background-color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
    margin-bottom: 16px !important;
    overflow: hidden !important;
    transition: box-shadow 0.3s ease;
}

.custom-accordion:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.14) !important;
}

fieldset { border: none !important; box-shadow: none !important; }

/* Text Chat */
#folium-chat .prose p, 
#folium-chat .prose li, 
#folium-chat .prose span,
#folium-chat p {
    color: #000000 !important; 
    font-family: 'Inter', 'Arial', sans-serif !important; 
    font-weight: 500 !important; 
    font-size: 17px !important;
    line-height: 1.6 !important;
}
#folium-chat .prose strong, #folium-chat strong, #folium-chat b {
    font-weight: 800 !important; 
    color: #000000 !important;
}
#folium-chat .message.user, #folium-chat .user {
    background-color: #e6fced !important;
    border: 2px solid #2e7d32 !important;
}
#folium-chat .message.bot, #folium-chat .bot {
    background-color: #f2faf4 !important;
    border: 2px solid #a3e0b7 !important;
}
#folium-chat .message hr {
    border-color: #a3e0b7 !important;
    border-width: 1px !important;
}
"""
#Theme of the System
my_theme = gr.themes.Soft(primary_hue="green").set(
    body_text_color="#000000"
)

with gr.Blocks(title="Folium AI", theme=my_theme, css=custom_css) as demo:
    active_chat_state = gr.State("")
    gr.HTML("<div class='logo'><h1 style='color:#2e7d32; font-weight: 900; font-size: 1.8em; margin:0;'>🌿 FOLIUM AI</h1></div>")
    with gr.Row():
        # Left Panel (Menu)
        with gr.Column(scale=3, min_width=250, elem_classes=["custom-panel"]):
            mode = gr.Radio(["RAG", "Basic", "Summarize"], label="Mode", value="Basic")
            
            with gr.Row(equal_height=False, elem_classes=["no-wrap-row"]):
                model_dropdown = gr.Dropdown(choices=get_installed_models(), value="qwen2.5:1.5b", label="AI Model", scale=4, min_width=120)
                refresh_model_btn = gr.Button("🔄 Refresh", scale=1, min_width=50, elem_classes=["refresh-btn"])
            
            with gr.Accordion("📂 Riwayat Obrolan", open=False, elem_classes=["custom-accordion"]):
                chat_dropdown = gr.Dropdown(choices=get_saved_chats(), label="Pilih & Edit Obrolan", allow_custom_value=True, interactive=True)
                with gr.Row():
                    load_btn = gr.Button("Buka", size="sm")
                    del_chat_btn = gr.Button("Hapus", variant="stop", size="sm")
        
            with gr.Accordion("⚙️ Pengaturan Prompt", open=False, elem_classes=["custom-accordion"]):
                system_prompt_input = gr.Textbox(value="Anda adalah asisten akademik yang ahli.", label="System Prompt", lines=2)
                
            with gr.Accordion("📚 Dokumen Sekolah", open=False, elem_classes=["custom-accordion"]):
                upload_button = gr.File(label="Upload Dokumen (PDF, Word, PPTX)", file_count="multiple", file_types=[".pdf", ".docx", ".doc", ".pptx", ".ppt"])
                db_status = gr.Textbox(value=get_db_status(), label="Status DB", interactive=False)
                delete_db_btn = gr.Button("🗑️ Kosongkan Database", variant="stop")
                
                upload_button.upload(upload_file, inputs=[upload_button], outputs=[db_status]).then(get_db_status, outputs=[db_status])
                delete_db_btn.click(clear_db, outputs=[db_status])

        # Right Panel (Menu)
        with gr.Column(scale=7, min_width=300, elem_classes=["custom-panel"]):
            chatbot = gr.Chatbot(height=500, label="Pusat Belajar", elem_id="folium-chat")
            
            with gr.Row():
                msg_input = gr.Textbox(show_label=False, placeholder="Ketik pertanyaan di sini...", scale=7)
                submit_btn = gr.Button("Kirim ➤", scale=1, variant="primary")
                stop_btn = gr.Button("🛑 Stop", scale=1, variant="stop", visible=False)
            
            with gr.Row():
                new_chat_btn = gr.Button("💬 Chat Baru")
                save_chat_btn = gr.Button("💾 Simpan Chat Ini")

            # --- Events ---
            refresh_model_btn.click(fn=lambda: gr.Dropdown(choices=get_installed_models()), outputs=[model_dropdown])
            chat_dropdown.change(direct_rename_chat, inputs=[chat_dropdown, active_chat_state], outputs=[chat_dropdown, active_chat_state])
            
            def hide_submit_show_stop():
                return gr.update(visible=False), gr.update(visible=True)
            
            def show_submit_hide_stop():
                return gr.update(visible=True), gr.update(visible=False)

            send_submit = msg_input.submit(
                hide_submit_show_stop, outputs=[submit_btn, stop_btn], queue=False
            ).then(
                user_sends_message, [msg_input, chatbot], [msg_input, chatbot], queue=False
            ).then(
                ai_responds, [chatbot, mode, system_prompt_input, model_dropdown], chatbot
            )
            send_submit.then(show_submit_hide_stop, outputs=[submit_btn, stop_btn], queue=False)

            send_click = submit_btn.click(
                hide_submit_show_stop, outputs=[submit_btn, stop_btn], queue=False
            ).then(
                user_sends_message, [msg_input, chatbot], [msg_input, chatbot], queue=False
            ).then(
                ai_responds, [chatbot, mode, system_prompt_input, model_dropdown], chatbot
            )
            send_click.then(show_submit_hide_stop, outputs=[submit_btn, stop_btn], queue=False)
            
            stop_btn.click(
                fn=None, inputs=None, outputs=None, cancels=[send_submit, send_click]
            ).then(
                show_submit_hide_stop, outputs=[submit_btn, stop_btn], queue=False
            )
            
            new_chat_btn.click(
                clear_current_chat, outputs=[chatbot, active_chat_state], cancels=[send_submit, send_click]
            ).then(
                show_submit_hide_stop, outputs=[submit_btn, stop_btn], queue=False
            )
            
            def load_and_set_active(chat_name):
                return load_chat(chat_name), chat_name
                
            save_chat_btn.click(save_chat, inputs=[chatbot], outputs=[chat_dropdown, active_chat_state])
            load_btn.click(load_and_set_active, inputs=[chat_dropdown], outputs=[chatbot, active_chat_state])
            del_chat_btn.click(delete_saved_chat, inputs=[chat_dropdown], outputs=[chat_dropdown, chatbot, active_chat_state])

#Launch the System (Searching for Port)
if __name__ == "__main__":
    import sys
    if sys.stdout is None: sys.stdout = open(os.devnull, "w")
    if sys.stderr is None: sys.stderr = open(os.devnull, "w")
    demo.launch(inbrowser=True, quiet=True)