# Álbum de Figurinhas da Copa 2026

Professor: Murilo Zanini

Aluno: Davi Nascimento de Jesus

Este repositório é referente à Atividade Ponderada 3, desenvolvida durante o encontro de instrução de computação da semana 7. A proposta era construir uma API para trabalhar com figurinhas da Copa do Mundo de 2026, aplicando conceitos de Clean Code, separação em camadas, injeção de dependência, erros de domínio nomeados e conexão com um banco SQLite local.

## Como rodar

Para rodar o projeto localmente, é preciso instalar as dependências e iniciar o servidor pelo arquivo `main.py`.

```bash
pip install -r requirements.txt
python main.py
```

Depois disso, a API fica disponível em `http://localhost:8080` e a documentação interativa do Swagger em `http://localhost:8080/docs`. O FastAPI foi escolhido também por esse motivo, já que facilita a validação manual dos endpoints durante o desenvolvimento.

