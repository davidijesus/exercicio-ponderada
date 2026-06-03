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

## Contexto e escolhas iniciais

Como o exercício anterior já utilizava separação entre camadas com responsabilidades distintas, com a permissão do professor, utilizei como base o repositório que tinha desenvolvido para a atividade anterior. Essa base já seguia a estrutura Domain, Repository, Service e Handler, então o principal trabalho foi adaptar o domínio antigo, que era de registro de gastos, para o novo domínio de figurinhas.

Python foi escolhido principalmente por familiaridade com a linguagem e por permitir trabalhar com SQLite local de forma simples. Embora o Python já tenha a biblioteca `sqlite3`, optei por usar SQLAlchemy para organizar melhor a persistência, evitando espalhar SQL manual pelo projeto e mantendo a regra de negócio longe dos detalhes de infraestrutura.

## Organização do domínio

O arquivo `domain/figurinha.py` concentra o vocabulário principal da aplicação. Nele, criei a entidade `Figurinha` com os campos exigidos no enunciado: `id`, `numero`, `tipo`, `posicao`, `updated_at` e `created_at`. O `id` é gerado pelo banco, enquanto `created_at` e `updated_at` são controlados pelo servidor.

Para evitar strings soltas no código, criei os enums `FigurinhaTipo` e `FigurinhaPosicao`. 

Os tipos aceitos são:

- `comum`
- `brilhante`
- `legends_ouro`
- `legends_bronze` 

As posições aceitas são:
- `Goleiro`
- `Zagueiro`
- `Meio-campista`
- `Atacante`

Essa decisão deixa os valores válidos explícitos e reduz validações repetidas.

Também separei a entidade dos DTOs de entrada. A entidade `Figurinha` representa o registro completo, enquanto `CreateFigurinhaRequest` e `UpdateFigurinhaRequest` representam apenas o que o cliente pode enviar: `numero`, `tipo` e `posicao`. Assim, o cliente não controla campos internos como `id`, `created_at` ou `updated_at`.

## Camadas e responsabilidades de cada uma delas

Na camada de Repository, separei o contrato da implementação. O arquivo `repository/figurinha_repository.py` define a interface `FigurinhaRepository`, enquanto `repository/figurinha_repo.py` implementa esse contrato com SQLAlchemy. Essa separação aplica o princípio de inversão de dependência: o Service depende de uma abstração, não diretamente do banco de dados.

Na camada de Service, implementei as regras de negócio em `service/figurinha_service.py`. O Service valida campos obrigatórios, confere se `tipo` e `posicao` pertencem aos enums, valida filtros de listagem e verifica se o `id` existe antes de buscar, atualizar ou deletar. Também é nessa camada que `created_at` e `updated_at` são preenchidos automaticamente.

Os erros de domínio também foram nomeados no Service. Criei `FigurinhaNotFoundError`, `RequiredFieldError`, `InvalidTipoError` e `InvalidPosicaoError` para deixar mais claro o motivo de cada falha e permitir que o Handler converta esses erros para os status HTTP corretos.

No Handler, implementei `handler/figurinha_handler.py` com o prefixo `/figurinha`, conforme o enunciado. Essa camada conhece FastAPI, corpo JSON, parâmetros de rota, filtros de query e status HTTP, mas não contém regra de negócio. Ela apenas recebe a requisição, monta os DTOs, chama o Service e transforma o resultado em resposta HTTP.

