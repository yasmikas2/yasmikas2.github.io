from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'segredo_suivivital'

CAMINHO_CADASTRO = os.path.join('database', 'alunos.json')
CAMINHO_FREQUENCIA = os.path.join('database', 'frequencia.json')
CAMINHO_FALTAS = os.path.join('database', 'faltas.json')

# Criar arquivos se não existirem
for caminho, vazio in [(CAMINHO_CADASTRO, []), (CAMINHO_FREQUENCIA, {}), (CAMINHO_FALTAS, {})]:
    if not os.path.exists(caminho):
        with open(caminho, 'w') as f:
            json.dump(vazio, f)

def carregar_alunos():
    with open(CAMINHO_CADASTRO, 'r') as f:
        return json.load(f)

def salvar_aluno(aluno):
    alunos = carregar_alunos()
    alunos.append(aluno)
    with open(CAMINHO_CADASTRO, 'w') as f:
        json.dump(alunos, f, indent=4)

def remover_aluno(cpf):
    alunos = carregar_alunos()
    alunos = [aluno for aluno in alunos if aluno['cpf'] != cpf]
    with open(CAMINHO_CADASTRO, 'w') as f:
        json.dump(alunos, f, indent=4)

def calcular_faltas(cpf, presencas):
    hoje = datetime.today()
    inicio = datetime(hoje.year, hoje.month, 1)
    dias_uteis = []

    while inicio <= hoje:
        if inicio.weekday() < 5:  # Dias úteis (segunda a sexta)
            dias_uteis.append(inicio.strftime('%Y-%m-%d'))
        inicio += timedelta(days=1)

    faltas = list(set(dias_uteis) - set(presencas))
    return sorted(faltas)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/desenvolvedores')
def desenvolvedores():
    return render_template('desenvolvedores.html')

@app.route('/cadastro_aluno', methods=['GET', 'POST'])
def cadastro_aluno():
    if request.method == 'POST':
        aluno = {
            'nome': request.form['nome'],
            'nascimento': request.form['nascimento'],
            'cpf': request.form['cpf'],
            'email': request.form['email'],
            'genero': request.form['genero']
        }
        salvar_aluno(aluno)
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login_aluno'))
    return render_template('cadastro_aluno.html')

@app.route('/login_aluno', methods=['GET', 'POST'])
def login_aluno():
    if request.method == 'POST':
        cpf = request.form['cpf']
        email = request.form['email']
        alunos = carregar_alunos()
        for aluno in alunos:
            if aluno['cpf'] == cpf and aluno['email'] == email:
                session['cpf'] = cpf
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('menu_aluno'))
        flash('CPF ou e-mail inválido.', 'danger')
    return render_template('login_aluno.html')

@app.route('/menu_aluno')
def menu_aluno():
    cpf = session.get('cpf')
    if not cpf:
        return redirect(url_for('login_aluno'))

    # Carrega os dados do aluno pelo CPF
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a['cpf'] == cpf), None)

    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('login_aluno'))

    nome = aluno.get('nome', 'Aluno')

    # Carregar presenças
    with open(CAMINHO_FREQUENCIA, 'r') as f:
        frequencias = json.load(f)
    presencas = frequencias.get(cpf, [])

    # Calcular faltas
    faltas = calcular_faltas(cpf, presencas)

    return render_template(
        'menu_aluno.html',
        nome=nome,
        cpf=cpf,
        presencas=presencas,
        faltas=faltas
    )

@app.route('/registrar_presenca', methods=['POST'])
def registrar_presenca():
    cpf = request.form['cpf']
    data = request.form['data']
    tipo = request.form['tipo']  # Tipo pode ser 'presenca' ou 'falta'

    # Carregar as presenças e faltas
    with open(CAMINHO_FREQUENCIA, 'r') as f:
        frequencias = json.load(f)

    with open(CAMINHO_FALTAS, 'r') as f:
        faltas = json.load(f)

    # Alterar a lista de presença ou falta
    if tipo == 'presenca':
        if cpf not in frequencias:
            frequencias[cpf] = []
        if data not in frequencias[cpf]:
            frequencias[cpf].append(data)
        if data in faltas.get(cpf, []):
            faltas[cpf].remove(data)
    elif tipo == 'falta':
        if cpf not in faltas:
            faltas[cpf] = []
        if data not in faltas[cpf]:
            faltas[cpf].append(data)
        if data in frequencias.get(cpf, []):
            frequencias[cpf].remove(data)

    # Salvar novamente as presenças e faltas
    with open(CAMINHO_FREQUENCIA, 'w') as f:
        json.dump(frequencias, f, indent=4)

    with open(CAMINHO_FALTAS, 'w') as f:
        json.dump(faltas, f, indent=4)

    return 'Status alterado com sucesso!', 200

@app.route('/login_gestor', methods=['GET', 'POST'])
def login_gestor():
    if request.method == 'POST':
        flash('Login gestor realizado (simulado)', 'success')
        return redirect(url_for('menu_gestor'))
    return render_template('login_gestor.html')

@app.route('/menu_gestor')
def menu_gestor():
    with open(CAMINHO_FREQUENCIA, 'r') as f:
        frequencias = json.load(f)

    with open(CAMINHO_FALTAS, 'r') as f:
        faltas = json.load(f)

    labels = list(frequencias.keys())
    valores = [len(frequencias[cpf]) for cpf in labels]
    faltas_valores = [len(faltas.get(cpf, [])) for cpf in labels]

    return render_template('menu_gestor.html', labels=labels, valores=valores, faltas=faltas_valores)

@app.route('/perfil_gestor')
def perfil_gestor():
    return render_template('perfil_gestor.html')

@app.route('/perfil_aluno')
def perfil_aluno():
    return render_template('perfil_aluno.html')

@app.route('/treinos')
def treinos():
    return render_template('treinos.html')

@app.route('/peito_triceps')
def peito_triceps():
    return render_template('peito_triceps.html')

@app.route('/costas_biceps')
def costas_biceps():
    return render_template('costas_biceps.html')

@app.route('/ombro_abdomen')
def ombro_abdomen():
    return render_template('ombro_abdomen.html')

@app.route('/pernas')
def pernas():
    return render_template('pernas.html')

@app.route('/gluteo')
def gluteo():
    return render_template('gluteo.html')

@app.route('/alunos')
def ver_alunos():
    alunos = carregar_alunos()

    if os.path.exists(CAMINHO_FREQUENCIA):
        with open(CAMINHO_FREQUENCIA, 'r') as f:
            frequencias = json.load(f)
    else:
        frequencias = {}

    if os.path.exists(CAMINHO_FALTAS):
        with open(CAMINHO_FALTAS, 'r') as f:
            faltas = json.load(f)
    else:
        faltas = {}

    # Anexar número de presenças e faltas por aluno
    for aluno in alunos:
        cpf = aluno.get('cpf')
        aluno['presencas'] = len(frequencias.get(cpf, []))
        aluno['faltas'] = len(faltas.get(cpf, []))

        # Garante que os campos "nascimento" e "genero" existam (para evitar KeyError se estiverem ausentes)
        aluno['nascimento'] = aluno.get('nascimento', 'Não informado')
        aluno['genero'] = aluno.get('genero', 'Não informado')

    return render_template('alunos.html', alunos=alunos)

@app.route('/evasao')
def evasao():
    alunos = carregar_alunos()

    if os.path.exists(CAMINHO_FREQUENCIA):
        with open(CAMINHO_FREQUENCIA, 'r') as f:
            frequencias = json.load(f)
    else:
        frequencias = {}

    if os.path.exists(CAMINHO_FALTAS):
        with open(CAMINHO_FALTAS, 'r') as f:
            faltas = json.load(f)
    else:
        faltas = {}

    # Anexar número de presenças e faltas por aluno
    alunos_com_mais_de_15_faltas = []
    for aluno in alunos:
        cpf = aluno.get('cpf')
        aluno['presencas'] = len(frequencias.get(cpf, []))
        aluno['faltas'] = len(faltas.get(cpf, []))

        aluno['nascimento'] = aluno.get('nascimento', 'Não informado')
        aluno['genero'] = aluno.get('genero', 'Não informado')

        if aluno['faltas'] > 15:
            alunos_com_mais_de_15_faltas.append(aluno)

    return render_template('evasao.html', alunos=alunos_com_mais_de_15_faltas)

# Rota para excluir aluno
@app.route('/excluir_aluno', methods=['POST'])
def excluir_aluno():
    cpf = request.form['cpf']
    
    # Remover o aluno de alunos.json
    remover_aluno(cpf)
    
    # Remover as frequências do aluno de frequencia.json
    if os.path.exists(CAMINHO_FREQUENCIA):
        with open(CAMINHO_FREQUENCIA, 'r') as f:
            frequencias = json.load(f)

        # Remover o aluno do arquivo de frequências
        if cpf in frequencias:
            del frequencias[cpf]

        with open(CAMINHO_FREQUENCIA, 'w') as f:
            json.dump(frequencias, f, indent=4)

    # Remover as faltas do aluno de faltas.json
    if os.path.exists(CAMINHO_FALTAS):
        with open(CAMINHO_FALTAS, 'r') as f:
            faltas = json.load(f)

        # Remover o aluno do arquivo de faltas
        if cpf in faltas:
            del faltas[cpf]

        with open(CAMINHO_FALTAS, 'w') as f:
            json.dump(faltas, f, indent=4)

    flash('Aluno excluído com sucesso!', 'success')
    return redirect(url_for('ver_alunos'))

if __name__ == '__main__':
    app.run(debug=True)
