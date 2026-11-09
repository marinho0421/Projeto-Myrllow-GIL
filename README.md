# Joia do Conhecimento (Pygame)

Jogo 2D de plataforma com rolagem lateral, em pixel art. Um garoto atrasado para a escola atravessa
3 mundos (Floresta/Biologia, Deserto/Matemática, Cidade Histórica/História), 3 níveis em cada,
coleta 9 Fragmentos do Conhecimento, forma a Joia e faz a prova final.

## Como iniciar
```
pip install -r requirements.txt     # só o pygame (>= 2.5), nenhum serviço externo
python main.py
```

## Controles
| Ação | Tecla |
|---|---|
| Mover | Setas ou A / D |
| Pular (segure para pular mais alto) | Espaço, seta cima ou W |
| Escalar cipós/escadas/muros | Cima/Baixo ou W/S perto da escada; Espaço pula dela |
| Correr | Shift |
| Pausar (reiniciar nível, configurações, progresso) | Esc |
| Menus / respostas dos desafios | Setas + Enter, teclas 1-3 ou mouse nos menus |
| Tela cheia | F11 |

## Novidades desta versão
- **Escolha de personagem** (antes de começar): João e Emília, com prévia lado a lado; a escolha é salva e pode ser trocada em *Configurações*.
  Emília usa a textura `maria-4x.png`; a folha de animação dela (`assets/sprites/emilia.png`, 12 quadros) é gerada por
  `tools/make_emilia_sheet.py` só a partir dessa textura. Mesma física, velocidade, pulo e hitbox para os dois.
- **Escolher fase** (menu inicial): modo de demonstração, qualquer fase direto, agrupada por bioma, com prévia do mapa e dificuldade.
  Não marca fases como concluídas nem concede fragmentos. *Jogar/Continuar* mantém a campanha com progressão normal.
- **Fases redesenhadas** (`game/level.py`): colinas, vales com caminho de baixo x corrente de plataformas, escadas/cipós/cordas/muros
  escaláveis, plataformas móveis (horizontais e elevadores), plataformas que caem, vespas/urubus/drones, passagens secretas com brindes,
  4-5 checkpoints por fase. `python tools/verify_levels.py [n]` (opcional `QUICK=1`) comprova com um bot que cada fase é completável.
- **Texturas** em `assets/textures/` (cópias; os originais não foram alterados): céu/árvores/gramado só na floresta; joias verde/amarela/roxa
  nos fragmentos (roxa = cidade, o último bioma); logo `schoolrushr-4x` na tela inicial (3x inteiro). Sem suavização.

```
main.py                  ponto de entrada
requirements.txt
assets/sprites/          protagonista.png (João) e emilia.png (12 quadros 29x54: parado, 6 de corrida, 5 de pulo) + imagem original
assets/textures/         texturas enviadas (*-4x.png)
tools/                   make_emilia_sheet.py, verify_levels.py
game/const.py            constantes, física e paletas dos mundos
game/lang.py             textos da interface + conteúdo educativo em pt / en / es
game/level.py            gerador de níveis (dificuldade cresce com o índice 0..8)
game/entities.py         Player (física), Enemy, Mover (plataforma móvel)
game/assets.py           carregamento em etapas (tela de carregamento real), fundos, inimigos, fragmentos
game/audio.py            efeitos sonoros gerados por código
game/save.py             progresso, idioma e som em ~/.joia_conhecimento_save.json
game/app.py              loop, estados e telas
```

## Como ampliar
- **Novo idioma:** inclua o código em `lang.LANGS` e uma posição extra em cada tupla de `UI` e em cada `CONTENT`.
- **Novo nível/mundo:** acrescente uma entrada em `CONTENT`, uma paleta em `const.WORLDS`, um fundo em `assets.bg_layers`
  e ajuste o número de níveis (`idx // 3` define o mundo).
- **Novo perigo:** crie um tipo em `level.build()` (função `hazard`).

## Observações de design
- Resolução lógica 640x360 ampliada com *nearest-neighbor* (pixels nítidos, sem suavização).
- Os 9 níveis são montados à mão com um construtor de segmentos (sempre iguais) e verificados com um bot de teste.
- Tocar em espinhos, inimigos ou cair em buracos reinicia no início do nível ou no último checkpoint.
- Cada nível tem um sinal "Você sabia?", um portão com desafio (precisa acertar para abrir) e o fragmento final.
