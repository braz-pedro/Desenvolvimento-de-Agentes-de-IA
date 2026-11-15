
import os
import sys
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

URL_BASE = os.getenv("LLM_BASE_URL", "https://llm-internal.softex:9001")
MODELO = os.getenv("LLM_MODEL", "qwen3.5:9b-q4_K_M")
VERIFICAR_SSL = os.getenv("LLM_VERIFY_SSL", "false").lower() == "true"
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

if not VERIFICAR_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def organizar_tarefas(texto):
    instrucao = (
        "Organize as anotacoes do usuario em uma lista de tarefas. "
        "Inclua os prazos quando forem mencionados. "
        "Nao invente informacoes. "
        "Responda em portugues brasileiro."
    )

    dados = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": instrucao},
            {"role": "user", "content": texto}
        ],
        "stream": False
    }

    resposta = requests.post(
        URL_BASE.rstrip("/") + "/api/chat",
        json=dados,
        timeout=TIMEOUT,
        verify=VERIFICAR_SSL
    )

    resposta.raise_for_status()
    resultado = resposta.json()

    return resultado["message"]["content"]


def main():
    print("OrganizaIA")
    print("Organize suas tarefas com inteligencia artificial.\n")

    texto = os.getenv("ORGANIZAIA_TEXTO", "").strip()

    if not texto and sys.stdin.isatty():
        texto = input("Digite suas anotacoes: ").strip()

    if not texto:
        print("Voce precisa informar alguma anotacao.")
        return

    print("\nOrganizando suas tarefas...\n")

    try:
        resultado = organizar_tarefas(texto)

        if not resultado.strip():
            print("A inteligencia artificial nao retornou tarefas.")
            return

        print("Suas tarefas:")
        print(resultado)

    except requests.exceptions.Timeout:
        print("A inteligencia artificial demorou muito para responder.")
        sys.exit(1)

    except requests.exceptions.RequestException:
        print("Nao foi possivel conectar com a inteligencia artificial.")
        sys.exit(1)

    except (KeyError, TypeError, ValueError):
        print("A inteligencia artificial retornou uma resposta invalida.")
        sys.exit(1)


if __name__ == "__main__":
    main()
