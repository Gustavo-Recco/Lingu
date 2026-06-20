# Lingu — Assistente Virtual de Estudos de Idiomas

> Aplicação desktop interativa para aprender **Inglês** e **Espanhol** com flashcards, quiz, exercícios de gramática, síntese de voz e feedback sonoro.

**Autor:** Gustavo Fernandes Recco  
**Disciplina:** Sistemas Multimídia — CIT7596  
**Instituição:** UFSC — Campus Araranguá — 2026  

---

## Como rodar

### Requisitos
- Python 3.10+
- matplotlib
- numpy
- pyttsx3

### 1. Instalar dependências
```
pip install matplotlib numpy pyttsx3   
```
ou
```
pip install -r requirements.txt
```

> `winsound` já vem com o Python no Windows, não precisa instalar.

> `urllib` e `queue` também já fazem parte da biblioteca padrão do Python.

### 2. Executar

```bash
py Lingu.py
```

---

## Estrutura do projeto

```
/
├── Lingu.py              # Aplicação principal
├── vocab_extra.json      # Palavras adicionadas pelo usuário (criado automaticamente)
└── README.md
```

---

## Telas

| Tela | Descrição |
|------|-----------|
| Seleção de idioma | Escolha entre Inglês e Espanhol |
| Menu | Acesso às atividades e estatísticas da sessão |
| Flashcards | Palavra, tradução, frase de exemplo e sua tradução em PT |
| Quiz | Múltipla escolha — traduz a palavra corretamente |
| Complete a Frase | Preenche a lacuna com a palavra gramatical correta |
| Progresso | Gráficos de acertos, erros e palavras estudadas por nível |
| Add Palavra | Cadastra novas palavras com auto-tradução via Google Translate (PT → idioma alvo), salvas entre sessões |

---

## Vocabulário base

3 palavras por idioma, todas de **Sistemas Multimídia**:

| EN | ES | PT |
|----|----|----|
| Multimedia | Multimedia | Multimídia |
| Compression | Compresion | Compressão |
| Resolution | Resolucion | Resolução |

Palavras extras são adicionadas pelo usuário no app e salvas em `vocab_extra.json`.

---

## Bibliotecas

| Biblioteca | Função |
|-----------|--------|
| `matplotlib` | Interface gráfica — botões, cards, gráficos |
| `numpy` | Gráficos de progresso |
| `pyttsx3` | Síntese de voz (TTS) em inglês e espanhol |
| `winsound` | Sons de acerto e erro (Windows) |
| `threading` | Áudio em paralelo sem travar a interface |
| `urllib` | Requisições ao Google Translate (sem API key) |
| `queue` | Comunicação thread-safe entre tradução e UI |
| `json` / `os` | Persistência das palavras do usuário |

---

## Observações

- O arquivo `vocab_extra.json` é criado automaticamente ao adicionar a primeira palavra.
- A auto-tradução usa o endpoint gratuito do Google Translate — requer conexão com internet.
- A voz em espanhol depende de uma voz instalada no sistema — se não encontrar, usa a voz padrão.
- Testado no Windows com Python 3.14.
