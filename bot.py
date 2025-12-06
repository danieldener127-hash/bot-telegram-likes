from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
import json, os
from openai import OpenAI # Importação da biblioteca OpenAI
import asyncio # Importação necessária para rodar set_my_commands

# Inicializa o cliente OpenAI (a chave API é carregada automaticamente do ambiente)
client = OpenAI()

LIKES_FILE = "likes.json"

# Funções utilitárias
def carregar_likes():
    if os.path.exists(LIKES_FILE):
        with open(LIKES_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_likes(data):
    with open(LIKES_FILE, "w") as f:
        json.dump(data, f)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot iniciado! Use /likes para adicionar curtidas e /ia para conversar com a IA.")

# Comando /likes
async def likes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = carregar_likes()

    if user_id not in data:
        data[user_id] = 0
    data[user_id] += 1
    salvar_likes(data)

    await update.message.reply_text("Likes enviados com sucesso!")

# Comando /ranking
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = carregar_likes()
    if not data:
        await update.message.reply_text("Ainda não há likes registrados.")
        return

    # Ordenar por número de likes (decrescente)
    ranking_text = "🏆 Ranking de Likes:\n\n"
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    for pos, (uid, likes) in enumerate(sorted_data, start=1):
        ranking_text += f"{pos}. Conta {uid} → {likes} likes\n"

    await update.message.reply_text(ranking_text)

# Comando /ia
async def ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verifica se há texto após o comando /ia
    if not context.args:
        await update.message.reply_text("Por favor, forneça uma pergunta após o comando /ia. Ex: /ia Qual a capital do Brasil?")
        return

    # Concatena os argumentos para formar a pergunta
    pergunta = " ".join(context.args)
    
    # Envia a pergunta para a API do OpenAI
    try:
        await update.message.reply_text("🤖 Pensando...")
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini", # Usando um modelo eficiente
            messages=[
                {"role": "system", "content": "Você é um assistente de IA prestativo e amigável."},
                {"role": "user", "content": pergunta}
            ]
        )
        
        resposta_ia = response.choices[0].message.content
        await update.message.reply_text(resposta_ia)
        
    except Exception as e:
        print(f"Erro ao chamar a API do OpenAI: {e}")
        await update.message.reply_text("Desculpe, houve um erro ao processar sua solicitação de IA.")


# Função que será chamada após a inicialização do bot
async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "Inicia o bot"),
        BotCommand("likes", "Adiciona um like à sua conta"),
        BotCommand("ranking", "Mostra o ranking de likes"),
        BotCommand("ia", "Converse com a Inteligência Artificial")
    ])

# Inicialização do bot
def main():
    app = Application.builder().token("8515435251:AAE7Msl9elE9G3Cxx4rc8WlZaY3Y6vZoSEk").post_init(post_init).build()

    # Registrar comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("likes", likes))
    app.add_handler(CommandHandler("ranking", ranking))
    app.add_handler(CommandHandler("ia", ia)) # Novo comando /ia

    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
