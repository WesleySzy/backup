import shutil
import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

# Configurar o logger
logging.basicConfig(filename='backup.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def obter_nome_pasta_destino(pasta_origem):
    data_hora_atual = datetime.datetime.now()
    data_hora_formatada = data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S")
    nome_pasta_origem = os.path.basename(pasta_origem)
    nome_pasta_destino = f"{nome_pasta_origem}_backup_{data_hora_formatada}"
    return nome_pasta_destino

def fazer_backup(pasta_origem, pasta_destino, manter_n_arquivos=6, intervalo_dias=3):
    try:
        # Verifique quando foi o último backup
        last_backup_file = os.path.join(pasta_destino, 'last_backup.txt')
        now = datetime.datetime.now()

        if os.path.exists(last_backup_file):
            with open(last_backup_file, 'r') as last_backup:
                last_backup_date = datetime.datetime.strptime(last_backup.read(), "%Y-%m-%d")

            # Verifique se é hora de fazer um novo backup
            if (now - last_backup_date).days < intervalo_dias:
                return  # Não é hora de fazer um novo backup ainda

        # Obtenha o nome da pasta de destino com a data e hora
        nome_pasta_destino = obter_nome_pasta_destino(pasta_origem)
        caminho_pasta_destino = os.path.join(pasta_destino, nome_pasta_destino)

        # Copie a pasta de origem para a pasta de destino
        shutil.copytree(pasta_origem, caminho_pasta_destino)

        print(f"Backup da pasta '{pasta_origem}' feito com sucesso em '{caminho_pasta_destino}'")

        # Registre uma mensagem de sucesso no log
        logging.info(f"Backup da pasta '{pasta_origem}' feito com sucesso em '{caminho_pasta_destino}'")

        # Verifique os arquivos existentes na pasta de destino
        arquivos_destino = os.listdir(caminho_pasta_destino)
        arquivos_destino = [os.path.join(caminho_pasta_destino, arquivo) for arquivo in arquivos_destino]
        arquivos_destino.sort(key=os.path.getctime, reverse=True)  # Classifique os arquivos por data de criação em ordem decrescente

        # Mantenha apenas os n arquivos mais recentes
        if len(arquivos_destino) > manter_n_arquivos:
            for arquivo in arquivos_destino[manter_n_arquivos:]:
                os.remove(arquivo)  # Exclua arquivos mais antigos

        # Atualize o arquivo de data do último backup
        with open(last_backup_file, 'w') as last_backup:
            last_backup.write(now.strftime("%Y-%m-%d"))

    except Exception as e:
        print(f"Erro ao fazer backup da pasta: {e}")


if __name__ == "__main__":
    pastas_para_backup = [
        {
            "pasta_origem": r"C:\Users\wesle\OneDrive\Área de Trabalho\Everlong Fotos",
            "pasta_destino": r"C:\Users\wesle\OneDrive\Área de Trabalho\Nuvem",
        },
        {
            "pasta_origem": r"C:\Users\wesle\OneDrive\Área de Trabalho\Diversos",
            "pasta_destino": r"C:\Users\wesle\OneDrive\Área de Trabalho\Nuvem",
        },
        {
            "pasta_origem": r"C:\Users\wesle\OneDrive\Área de Trabalho\dbz",
            "pasta_destino": r"C:\Users\wesle\OneDrive\Área de Trabalho\Nuvem",
        },
        # Adicione mais pastas de origem e destino conforme necessário
    ]
    
    for pasta in pastas_para_backup:
        fazer_backup(pasta["pasta_origem"], pasta["pasta_destino"])

        # Lê o conteúdo do arquivo de log
    with open('backup.log', 'r') as log_file:
        log_content = log_file.read()

    # Configurações de autenticação
    sender_email = "from"
    sender_password = "autenticação senha"
    receiver_email = "destino"

    # Configurar servidor SMTP do Gmail
    smtp_server = "smtp"
    smtp_port = 587  # Usar 465 para SSL ou 587 para TLS

    # Criar mensagem de e-mail
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "assunto"

    # Corpo do e-mail
    body = "mesagem"

    # Anexar o corpo do e-mail à mensagem
    msg.attach(MIMEText(body, "plain"))

    # Anexar o arquivo de log como anexo
    log_attachment = MIMEApplication(log_content)
    log_attachment.add_header('Content-Disposition', 'attachment', filename='backup.log')
    msg.attach(log_attachment)

    # Iniciar conexão SMTP e enviar e-mail
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Use esta linha para TLS
        # server.login(sender_email, sender_password)  # Faça login apenas se não estiver usando autenticação de dois fatores

        # Caso esteja usando autenticação de dois fatores, você precisa gerar uma senha de aplicativo e usá-la em vez da senha da conta
        # https://support.google.com/accounts/answer/185833?hl=en
        app_password = "senha do pass"
        server.login(sender_email, app_password)

        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("E-mail de confirmacao enviado com sucesso.")
    except Exception as e:
        print("Erro ao enviar e-mail:", str(e))
    finally:
        server.quit()

