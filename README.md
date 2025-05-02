# Know Your Fan 🦁🎮

**Desafio #2 – Know Your Fan [HARD]**

Este projeto foi desenvolvido como parte de um desafio para criar uma solução que colete, analise e valide informações de fãs de eSports — com foco em personalização de experiências por organizações como a FURIA.

## 🚀 Objetivo

Desenvolver um app web que:

- Coleta dados pessoais e interesses do usuário.
- Permite upload e validação de documentos com auxílio de inteligência artificial.
- Integra redes sociais e perfis de sites de eSports.
- Constrói um perfil rico e validado de fãs para futuras experiências personalizadas.

---

## 🧠 Funcionalidades

✅ **Cadastro e perfil do usuário**

- Nome, endereço, CPF, interesses em eSports.
- Histórico de atividades, eventos e compras.

✅ **Upload e Validação de Documentos (AI)**

- Upload de documentos de identidade.
- Validação automática via modelo de IA (base64).

✅ **Integração com Redes Sociais**

- Conexão com redes sociais para extrair:
  - Curtidas, páginas seguidas.
  - Interações com organizações como a FURIA.

✅ **Validação de perfis externos**

- Usuário insere links de perfis em sites de eSports.
- IA analisa o conteúdo e valida se é compatível com seu perfil.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11**
- **PostgreSQL Para Banco de Dados**
- **Flask**
- **Flask-Login / Flask-WTF**
- **SQLAlchemy**
- **Bootstrap**
- **Integração com modelo de IA para validação de documentos**
- **Base64 encoding para envio de imagens**
- **(Opcional)** APIs de redes sociais

---

## 📂 Estrutura do Projeto

## Know_Your_Fan/
├── app.py # App principal Flask
├── main.py # Entry point
├── models/ # Modelos de banco de dados
├── routes/ # Rotas (auth, profile, etc.)
├── templates/ # Templates HTML (Jinja)
├── static/ # Arquivos estáticos (CSS, JS)
├── uploads/ # Armazenamento temporário de documentos
├── requirements.txt # Dependências do projeto
└── README.md # Este arquivo


---

## ▶️ Como Rodar Localmente

### 1. Clone o repositório

git clone https://github.com/Miguel3074/Know_Your_Fan.git
cd know-your-fan

### 2. Crie e ative o ambiente virtual

python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate



### 3. Instale as dependências

pip install -r requirements.txt

### 4.Crie um Banco de dados Postgree

createdb -U postgres nome_do_banco

Preenher dai .ENV local com as informacoes

### 5. Rode a aplicação

python main.py
Acesse o link gerado

### 📌 Observações

A IA utilizada para validação de documentos pode ser substituída por uma API externa.

Integrações com redes sociais nao foi aplicada efetivamente por nao possuir acesso as apis de desenvolvedor de cada rede social

📬 Contato
Desenvolvido por Miguel dos Anjos Brack como parte do desafio "Know Your Fan" – FURIA.





