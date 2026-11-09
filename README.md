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
| Correr | Shift |
| Pausar (reiniciar nível, configurações, progresso) | Esc |
| Menus / respostas dos desafios | Setas + Enter, teclas 1-3 ou mouse nos menus |
| Tela cheia | F11 |

## Estrutura
```
main.py                  ponto de entrada
requirements.txt
assets/sprites/          protagonista.png (12 frames 29x54: parado, 6 de corrida, 5 de pulo) e a imagem original
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
- Os níveis são gerados por código com semente fixa (sempre iguais) em vez de mapas desenhados à mão;
  é a alternativa mais simples de manter e de ampliar. Todos os 9 foram verificados com um bot de teste.
- Tocar em espinhos, inimigos ou cair em buracos reinicia no início do nível ou no último checkpoint.
- Cada nível tem um sinal "Você sabia?", um portão com desafio (precisa acertar para abrir) e o fragmento final.
