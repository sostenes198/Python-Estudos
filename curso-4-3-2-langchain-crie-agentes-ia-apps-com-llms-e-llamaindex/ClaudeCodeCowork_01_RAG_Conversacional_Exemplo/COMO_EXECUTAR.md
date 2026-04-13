# Chat Conversacional com Memória RAG

## Instalar dependências

```bash
pip install chromadb sentence-transformers groq python-dotenv
```

## Configurar variável de ambiente

Crie um arquivo `.env` na raiz do projeto com:

```
GROQ_API_KEY=sua_chave_aqui
```

## Executar

```bash
python chat_com_memoria_rag.py
```

## Fluxo do script

```
Usuário digita → gera embedding da pergunta
                       ↓
              busca no ChromaDB os turnos
              mais similares semanticamente
                       ↓
              injeta contexto relevante no system
                       ↓
              LLM responde (messages só tem a pergunta atual)
                       ↓
              salva o turno como documento rico no ChromaDB
```

## Teste sugerido

1. Diga que seu computador Dell não liga
2. Fale sobre a luz laranja piscando
3. Mude de assunto (fale de qualquer outra coisa)
4. Diga "o problema voltou"

Observe como o script recupera os turnos 1 e 2 mesmo depois de outros assuntos.
