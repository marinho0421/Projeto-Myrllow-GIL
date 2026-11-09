"""Textos da interface e conteudo educativo (pt / en / es). Para novo idioma, adicione a tupla/chave."""
LANGS = ["pt", "en", "es"]
LANG_NAMES = {"pt": "Português", "en": "English", "es": "Español"}
cur = "pt"

UI = {  # chave: (pt, en, es)
 "title": ("Joia do Conhecimento", "Jewel of Knowledge", "Joya del Conocimiento"),
 "sub": ("Um atalho pela floresta para chegar à escola...", "A forest shortcut to reach school...", "Un atajo por el bosque hacia la escuela..."),
 "play": ("Jogar", "Play", "Jugar"), "cont": ("Continuar", "Continue", "Continuar"),
 "settings": ("Configurações", "Settings", "Configuración"), "quit": ("Sair", "Quit", "Salir"),
 "lang": ("Idioma", "Language", "Idioma"), "sound": ("Som", "Sound", "Sonido"),
 "on": ("Ligado", "On", "Activado"), "off": ("Desligado", "Off", "Apagado"),
 "back": ("Voltar", "Back", "Volver"), "loading": ("Carregando...", "Loading...", "Cargando..."),
 "enter": ("Enter para continuar", "Press Enter", "Pulsa Enter"),
 "paused": ("Pausa", "Paused", "Pausa"), "resume": ("Continuar", "Resume", "Continuar"),
 "restart": ("Reiniciar nível", "Restart level", "Reiniciar nivel"),
 "menu": ("Menu principal", "Main menu", "Menú principal"),
 "progress": ("Progresso da aventura", "Adventure progress", "Progreso de la aventura"),
 "controls": ("A/D ou setas: mover   Shift: correr   Espaço ou seta cima: pular   Esc: pausa",
              "A/D or arrows: move   Shift: run   Space or up arrow: jump   Esc: pause",
              "A/D o flechas: mover   Shift: correr   Espacio o flecha arriba: saltar   Esc: pausa"),
 "w1": ("Floresta — Biologia", "Forest — Biology", "Bosque — Biología"),
 "w2": ("Deserto — Matemática", "Desert — Math", "Desierto — Matemáticas"),
 "w3": ("Cidade Histórica — História", "Historic City — History", "Ciudad Histórica — Historia"),
 "level": ("Nível", "Level", "Nivel"),
 "goal": ("Evite os perigos e chegue ao Fragmento do Conhecimento!", "Avoid the dangers and reach the Knowledge Fragment!", "¡Evita los peligros y llega al Fragmento del Conocimiento!"),
 "fic": ("Os fatos históricos são reais; os portais e a Joia são fantasia.", "Historical facts are real; the portals and the Jewel are fiction.", "Los hechos históricos son reales; los portales y la Joya son fantasía."),
 "quiz": ("Desafio", "Challenge", "Desafío"),
 "quizhint": ("1-3 ou setas + Enter", "1-3 or arrows + Enter", "1-3 o flechas + Enter"),
 "wrong": ("Ainda não! Tente de novo.", "Not yet! Try again.", "¡Aún no! Inténtalo otra vez."),
 "right": ("Correto! O caminho se abriu.", "Correct! The way is open.", "¡Correcto! El camino se abrió."),
 "know": ("Você sabia?", "Did you know?", "¿Sabías que?"),
 "clear": ("Fragmento coletado! Um portal se abre...", "Fragment collected! A portal opens...", "¡Fragmento obtenido! Se abre un portal..."),
 "story1": ("Um garoto acorda atrasado: hoje tem prova de várias matérias na escola!", "A boy wakes up late: today there are exams at school!", "Un chico despierta tarde: ¡hoy hay exámenes en la escuela!"),
 "story2": ("No ponto, o ônibus já passou. Um desconhecido aparece: \"Há um atalho pela floresta!\"", "At the stop, the bus is gone. A stranger appears: \"There is a shortcut through the forest!\"", "En la parada, el autobús ya se fue. Un desconocido aparece: «¡Hay un atajo por el bosque!»"),
 "story3": ("No caminho, portais levam o garoto a outros lugares e épocas. Fragmentos do conhecimento formarão a Joia que o ajudará na prova final.", "On the way, portals take the boy to other places and times. Knowledge fragments will form the Jewel that helps him in the final exam.", "En el camino, portales llevan al chico a otros lugares y épocas. Los fragmentos del conocimiento formarán la Joya que lo ayudará en el examen final."),
 "jewel": ("Os 9 fragmentos se unem: nasce a Joia do Conhecimento!", "The 9 fragments unite: the Jewel of Knowledge is born!", "¡Los 9 fragmentos se unen: nace la Joya del Conocimiento!"),
 "exam": ("Prova final", "Final exam", "Examen final"),
 "score": ("Acertos", "Correct", "Aciertos"),
 "exam_ok": ("Aprovado! A Joia brilhou e você chegou à escola!", "Passed! The Jewel shone and you reached school!", "¡Aprobado! ¡La Joya brilló y llegaste a la escuela!"),
 "exam_bad": ("Quase! Revise e tente de novo.", "Almost! Review and try again.", "¡Casi! Repasa e inténtalo de nuevo."),
 "end": ("Fim", "The End", "Fin"),
 "end_text": ("Com a Joia do Conhecimento, o garoto venceu a prova. Obrigado por jogar!", "With the Jewel of Knowledge, the boy aced the exam. Thanks for playing!", "Con la Joya del Conocimiento, el chico superó el examen. ¡Gracias por jugar!"),
}

def T(k):
    return UI[k][LANGS.index(cur)]

# conteudo educativo: ans = indice da opcao correta; cada idioma: [fato, pergunta, op1, op2, op3]
CONTENT = [
 dict(ans=0,
  pt=["Plantas fazem fotossíntese: com luz do sol, água e ar, produzem o próprio alimento.", "O que a planta usa para fazer seu alimento?", "Luz do sol, água e ar", "Só pedras", "Só barulho"],
  en=["Plants do photosynthesis: with sunlight, water and air they make their own food.", "What does a plant use to make its food?", "Sunlight, water and air", "Only rocks", "Only noise"],
  es=["Las plantas hacen fotosíntesis: con luz solar, agua y aire fabrican su alimento.", "¿Qué usa una planta para hacer su alimento?", "Luz solar, agua y aire", "Solo piedras", "Solo ruido"]),
 dict(ans=1,
  pt=["Habitat é o lugar onde um animal encontra comida, água e abrigo.", "Qual é o habitat de um peixe?", "Deserto", "Rio ou lago", "Ninho de pássaro"],
  en=["A habitat is where an animal finds food, water and shelter.", "What is a fish's habitat?", "Desert", "River or lake", "Bird nest"],
  es=["Hábitat es donde un animal encuentra comida, agua y refugio.", "¿Cuál es el hábitat de un pez?", "Desierto", "Río o lago", "Nido de pájaro"]),
 dict(ans=2,
  pt=["Cadeia alimentar: o Sol ajuda a planta, o coelho come a planta e a raposa come o coelho.", "Na cadeia alimentar, quem é o produtor?", "Raposa", "Coelho", "Planta"],
  en=["Food chain: the Sun helps the plant, the rabbit eats the plant and the fox eats the rabbit.", "In a food chain, who is the producer?", "Fox", "Rabbit", "Plant"],
  es=["Cadena alimentaria: el Sol ayuda a la planta, el conejo come la planta y el zorro come al conejo.", "En la cadena alimentaria, ¿quién es el productor?", "Zorro", "Conejo", "Planta"]),
 dict(ans=1,
  pt=["Multiplicar é somar parcelas iguais: 6 × 7 = 7+7+7+7+7+7.", "Quanto é 9 × 6?", "56", "54", "45"],
  en=["Multiplying is adding equal parts: 6 × 7 = 7+7+7+7+7+7.", "What is 9 × 6?", "56", "54", "45"],
  es=["Multiplicar es sumar partes iguales: 6 × 7 = 7+7+7+7+7+7.", "¿Cuánto es 9 × 6?", "56", "54", "45"]),
 dict(ans=0,
  pt=["Um triângulo tem 3 lados. Em medidas, 1 metro tem 100 centímetros.", "Quantos centímetros tem 2 metros?", "200", "20", "2000"],
  en=["A triangle has 3 sides. In measures, 1 meter has 100 centimeters.", "How many centimeters are in 2 meters?", "200", "20", "2000"],
  es=["Un triángulo tiene 3 lados. En medidas, 1 metro tiene 100 centímetros.", "¿Cuántos centímetros hay en 2 metros?", "200", "20", "2000"]),
 dict(ans=2,
  pt=["Em um triângulo retângulo, a soma dos quadrados dos catetos é igual ao quadrado da hipotenusa: a² + b² = c².", "Catetos 3 e 4. Quanto mede a hipotenusa?", "6", "7", "5"],
  en=["In a right triangle, the sum of the squares of the legs equals the square of the hypotenuse: a² + b² = c².", "Legs are 3 and 4. How long is the hypotenuse?", "6", "7", "5"],
  es=["En un triángulo rectángulo, la suma de los cuadrados de los catetos es igual al cuadrado de la hipotenusa: a² + b² = c².", "Los catetos miden 3 y 4. ¿Cuánto mide la hipotenusa?", "6", "7", "5"]),
 dict(ans=1,
  pt=["Atenas, na Grécia Antiga, é conhecida como o berço da democracia.", "Qual cidade antiga é chamada de berço da democracia?", "Pompeia", "Atenas", "Cairo"],
  en=["Athens, in Ancient Greece, is known as the cradle of democracy.", "Which ancient city is called the cradle of democracy?", "Pompeii", "Athens", "Cairo"],
  es=["Atenas, en la Antigua Grecia, es conocida como la cuna de la democracia.", "¿Qué ciudad antigua se llama cuna de la democracia?", "Pompeya", "Atenas", "El Cairo"]),
 dict(ans=0,
  pt=["A Revolução Francesa começou em 1789, quando o povo de Paris tomou a Bastilha, uma antiga fortaleza.", "Em que ano começou a Revolução Francesa?", "1789", "1492", "1822"],
  en=["The French Revolution began in 1789, when the people of Paris took the Bastille, an old fortress.", "In what year did the French Revolution begin?", "1789", "1492", "1822"],
  es=["La Revolución Francesa comenzó en 1789, cuando el pueblo de París tomó la Bastilla, una antigua fortaleza.", "¿En qué año comenzó la Revolución Francesa?", "1789", "1492", "1822"]),
 dict(ans=2,
  pt=["O lema da Revolução Francesa: Liberdade, Igualdade, Fraternidade. Isso é real! Já os portais e a Joia são ficção.", "Qual era o lema da Revolução Francesa?", "Ordem e Progresso", "Paz e Pão", "Liberdade, Igualdade, Fraternidade"],
  en=["The motto of the French Revolution: Liberty, Equality, Fraternity. That is real! The portals and the Jewel are fiction.", "What was the motto of the French Revolution?", "Order and Progress", "Peace and Bread", "Liberty, Equality, Fraternity"],
  es=["El lema de la Revolución Francesa: Libertad, Igualdad, Fraternidad. ¡Eso es real! Los portales y la Joya son ficción.", "¿Cuál era el lema de la Revolución Francesa?", "Orden y Progreso", "Paz y Pan", "Libertad, Igualdad, Fraternidad"]),
]

def content(i):
    c = CONTENT[i]; t = c[cur]
    return dict(fact=t[0], q=t[1], opts=t[2:5], ans=c["ans"])
