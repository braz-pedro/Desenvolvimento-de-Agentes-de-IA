
import os
import sys
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

URL_BASE = os.getenv(
    "LLM_BASE_URL",
    "https://llm-internal.softex:9001"
)
MODELO = os.getenv(
    "LLM_MODEL",
    "qwen3.5:9b-q4_K_M"
)
VERIFICAR_SSL = os.getenv(
    "LLM_VERIFY_SSL", "true"
).lower() == "true"

TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

if not VERIFICAR_SSL:
    urllib3.disable_warnings(
        urllib3.exceptions.InsecureRequestWarning
    )


def organizar_tarefas(texto):
    """Envia uma anotação ao LLM e retorna as tarefas."""

    instrucao = (
        "Você é um organizador de tarefas. "
        "Transforme o texto recebido em uma lista "
        "numerada de tarefas, indicando os prazos "
        "mencionados. Não invente informações. "
        "Responda em português brasileiro."
    )

    payload = {
        "model": MODELO,
        "messages": [
            {
                "role": "system",
                "content": instrucao
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        "stream": False
    }

    resposta = requests.post(
        f"{URL_BASE.rstrip('/')}/api/chat",
        json=payload,
        timeout=TIMEOUT,
        verify=VERIFICAR_SSL
    )

    resposta.raise_for_status()

    dados = resposta.json()
    return dados["message"]["content"]


def main():
    print("       ORGANIZADOR")
  

   texto = os.getenv("ORGANIZAIA_TEXTO", "").strip()

    if not texto:
        if sys.stdin.isatty():
           texto = input(
              "\nDigite suas anotacoes:\n> "
             ).strip()

    if not texto:
        print("\nDigite um texto valido.")
        return

    print("\nProcessando suas tarefas...\n")

    try:
        resultado = organizar_tarefas(texto)

        if not resultado.strip():
            print("O modelo retornou uma resposta vazia.")
            return

        print("TAREFAS ORGANIZADAS")
        print("-" * 45)
        print(resultado)

    except requests.exceptions.RequestException:
        print("Nao foi possivel acessar o LLM. Verifique a conexao e o servidor."
        )
        sys.exit(1)

    except (KeyError, TypeError, ValueError):
        print("O LLM retornou uma resposta inesperada.")
        sys.exit(1)


if __name__ == "__main__":
    main()
