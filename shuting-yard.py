from graphviz import Digraph

class Nodo:
    def __init__(self, valor, izquierda=None, derecha=None):
        self.valor = valor
        self.izquierda = izquierda
        self.derecha = derecha

# --------------------
# PARTE 1: Funciones de Lab anterior
# --------------------
def expandir_clases(expr):
    resultado = ''
    i = 0
    while i < len(expr):
        if expr[i] == '\\':
            if i + 1 < len(expr):
                resultado += expr[i:i+2]
                i += 2
        elif expr[i] == '[':
            i += 1
            contenido = ''
            while i < len(expr) and expr[i] != ']':
                contenido += expr[i]
                i += 1
            if i < len(expr) and contenido:
                resultado += '(' + '|'.join(contenido) + ')'
                i += 1
            else:
                raise ValueError("Clase de caracteres sin cerrar o vacía")
        else:
            resultado += expr[i]
            i += 1
    return resultado

def insertar_concatenaciones(expr):
    resultado = ''
    i = 0
    while i < len(expr):
        c1 = expr[i]
        resultado += c1
        if c1 == '\\':
            i += 1
            if i < len(expr):
                resultado += expr[i]
        elif i + 1 < len(expr):
            c2 = expr[i + 1]
            if ((c1 not in {'(', '|'} and c2 not in {'*', '+', '?', '|', ')'})
                or (c1 in {'*', '+', '?'} and c2 not in {'*', '+', '?', '|', ')'})
                or (c1 == ')' and c2 == '(')
                or (c1 == ')' and c2.isalnum())
                or (c1.isalnum() and c2 == '(')):
                resultado += '.'
        i += 1
    return resultado

def expandir_operadores(expr):
    i = 0
    resultado = ''
    while i < len(expr):
        if expr[i] == '\\':
            if i + 1 < len(expr):
                resultado += expr[i:i+2]
                i += 2
            else:
                raise ValueError("Escape incompleto")
        elif expr[i] == '+':
            if resultado and resultado[-1] == ')':
                count = 0
                j = len(resultado) - 1
                while j >= 0:
                    if resultado[j] == ')':
                        count += 1
                    elif resultado[j] == '(':
                        count -= 1
                        if count == 0:
                            break
                    j -= 1
                grupo = resultado[j:]
                resultado += '.' + grupo + '*'
            else:
                prev = resultado.rstrip('.')[-1]
                resultado += '.' + prev + '*'
            i += 1
        elif expr[i] == '?':
            if resultado and resultado[-1] == ')':
                resultado += '|ε'
            else:
                resultado += '|ε'
            i += 1
        else:
            resultado += expr[i]
            i += 1
    return resultado

def shunting_yard(regex):
    salida = []
    pila = []
    precedencia = {'*': 3, '.': 2, '|': 1}
    operadores = set(precedencia.keys())
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == ' ':
            i += 1
            continue
        if c == '\\':
            if i + 1 < len(regex):
                salida.append('\\' + regex[i + 1])
                i += 2
            else:
                raise ValueError("Secuencia de escape incompleta")
        elif c.isalnum() or c in {'ε', '@', '.', '{', '}'}:
            salida.append(c)
            i += 1
        elif c == '(':
            pila.append(c)
            i += 1
        elif c == ')':
            while pila and pila[-1] != '(':
                salida.append(pila.pop())
            if pila:
                pila.pop()
                i += 1
            else:
                raise ValueError("Falta paréntesis de apertura")
        elif c in operadores:
            while (pila and pila[-1] in operadores and precedencia[c] <= precedencia[pila[-1]]):
                salida.append(pila.pop())
            pila.append(c)
            i += 1
        else:
            raise ValueError(f"Carácter no reconocido: '{c}'")
    while pila:
        top = pila.pop()
        if top in {'(', ')'}:
            raise ValueError("Paréntesis desbalanceados.")
        salida.append(top)
    return salida

# --------------------
# PARTE 2: Postfix → Árbol
# --------------------
def postfix_a_arbol(postfijo):
    pila = []
    for token in postfijo:
        if token in {'*'}:
            nodo = Nodo(token, izquierda=pila.pop())
            pila.append(nodo)
        elif token in {'.', '|'}:
            derecha = pila.pop()
            izquierda = pila.pop()
            nodo = Nodo(token, izquierda, derecha)
            pila.append(nodo)
        else:
            pila.append(Nodo(token))
    return pila[0]

# --------------------
# PARTE 3: Dibujar árbol
# --------------------
def dibujar_arbol(nodo, nombre_archivo):
    dot = Digraph()
    def agregar_nodos_edges(nodo, id_actual=0):
        nodo_id = str(id_actual)
        dot.node(nodo_id, nodo.valor)
        next_id = id_actual
        if nodo.izquierda:
            next_id += 1
            dot.edge(nodo_id, str(next_id))
            next_id = agregar_nodos_edges(nodo.izquierda, next_id)
        if nodo.derecha:
            next_id += 1
            dot.edge(nodo_id, str(next_id))
            next_id = agregar_nodos_edges(nodo.derecha, next_id)
        return next_id
    agregar_nodos_edges(nodo)
    dot.render(nombre_archivo, format='png', cleanup=True)

# --------------------
# PARTE 4: Procesamiento completo
# --------------------
def procesar_archivo(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        lineas = archivo.readlines()
    for i, linea in enumerate(lineas):
        original = linea.strip()
        if not original:
            continue
        print(f"\nProcesando expresión [{i+1}]: {original}")
        try:
            clase_expandida = expandir_clases(original)
            con_concat = insertar_concatenaciones(clase_expandida)
            expandida = expandir_operadores(con_concat)
            postfijo = shunting_yard(expandida)
            print(f"Postfix: {' '.join(postfijo)}")
            arbol = postfix_a_arbol(postfijo)
            nombre_img = f"arbol_exp_{i+1}"
            dibujar_arbol(arbol, nombre_img)
            print(f"Árbol guardado en {nombre_img}.png")
        except Exception as e:
            print(f"Error: {e}")
    print("\n🎉 ¡Procesamiento finalizado!")

# Ejecutar
procesar_archivo("input.txt")
