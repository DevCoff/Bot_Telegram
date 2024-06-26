import telebot
import os

CHAVE_API = "sua_chave_api"

bot = telebot.TeleBot(CHAVE_API)

# Dicionário para armazenar o estado de cada usuário
user_states = {}

# Estados possíveis
STATE_WAITING_FOR_ADDRESS = 1
STATE_IDLE = 0

@bot.message_handler(commands=["start", "ajuda"])
def ajuda_limpeza(mensagem):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("1. Solicitar ajuda com limpeza")
    markup.row("2. Finalizar conversa")
    bot.send_message(mensagem.chat.id, "Selecione uma opção:", reply_markup=markup)
    user_states[mensagem.chat.id] = STATE_IDLE

@bot.message_handler(func=lambda message: message.text == "1. Solicitar ajuda com limpeza")
def solicitar_limpeza(mensagem):
    bot.send_message(mensagem.chat.id, "Por favor, envie seu endereço completo, contendo rua, número, CEP, cidade e também um telefone para contato. Responda a esta mensagem com essas informações.")
    user_states[mensagem.chat.id] = STATE_WAITING_FOR_ADDRESS

@bot.message_handler(func=lambda message: message.text == "2. Finalizar conversa")
def finalizar_conversa(mensagem):
    bot.send_message(mensagem.chat.id, "Conversa finalizada. Digite /ajuda para iniciar uma nova conversa.")
    user_states[mensagem.chat.id] = STATE_IDLE

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == STATE_WAITING_FOR_ADDRESS)
def processar_endereco(mensagem):
    endereco = mensagem.text.upper()  # Convertendo o endereço para maiúsculas
    try:
        if salvar_endereco(endereco):
            bot.send_message(mensagem.chat.id, f"Solicitação de ajuda comunitária para limpeza recebida. Endereço: {endereco}.")
            bot.send_message(mensagem.chat.id, "Obrigado por solicitar ajuda comunitária para limpeza de casas! Em breve, entraremos em contato com você para organizar os detalhes.")
            bot.send_message(mensagem.chat.id, "Lembre-se: juntos, podemos fazer a diferença na nossa comunidade!")
        else:
            bot.send_message(mensagem.chat.id, "Ocorreu um erro ao salvar o endereço.")
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Ocorreu um erro ao salvar o endereço: {str(e)}")
    user_states[mensagem.chat.id] = STATE_IDLE  # Resetar o estado do usuário

def salvar_endereco(endereco):
    try:
        if not os.path.exists("enderecos.txt"):
            with open("enderecos.txt", "w") as arquivo:
                pass  # Cria o arquivo se não existir

        with open("enderecos.txt", "r+") as arquivo:
            enderecos = arquivo.readlines()
            substituido = False
            for i, linha in enumerate(enderecos):
                if linha.strip() == endereco:
                    enderecos[i] = endereco + "\n"
                    substituido = True
                    break
            if not substituido:
                enderecos.append(endereco + "\n")
            arquivo.seek(0)
            arquivo.truncate()
            arquivo.writelines(enderecos)
        return True
    except Exception as e:
        raise Exception(f"Erro ao salvar o endereço: {str(e)}")

@bot.message_handler(func=lambda message: True)
def default_response(mensagem):
    if mensagem.text == "1. Solicitar ajuda com limpeza":
        solicitar_limpeza(mensagem)
    elif mensagem.text == "2. Finalizar conversa":
        finalizar_conversa(mensagem)
    else:
        bot.send_message(mensagem.chat.id, "Opção inválida. Por favor, selecione uma opção válida.")
        ajuda_limpeza(mensagem)

bot.polling()
