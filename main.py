from flask import Flask, render_template, request, redirect, flash, url_for, session
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\coisafinanca\FINANCA.FDB'
user = 'sysdba'
password = 'sysdba'


con = fdb.connect(host=host, database=database, user=user, password=password)


@app.route('/criar_conta')
def criar_conta():
    return render_template('criar_conta.html')


@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    # Criando o cursor
    cursor = con.cursor()

    try:
        # Verificar se o usuario já existe com a combinação de fonte e data
        cursor.execute("SELECT 1 FROM usuario WHERE EMAIL = ?", (email,))
        if cursor.fetchone():  # Se existir algum registro
            flash("Erro: Conta já cadastrada.", "error")
            return redirect(url_for('criar_conta'))

        # Inserir o novo registro
        cursor.execute("INSERT INTO usuario (NOME, EMAIL, SENHA) VALUES (?, ?, ?)",
                       (nome, email, senha))
        con.commit()
        flash("Usuario criado com sucesso!", "success")
    except Exception as e:
        # Se ocorrer um erro, exibe uma mensagem de erro
        flash(f"Erro ao cadastrar usuario: {str(e)}", "error")
        con.rollback()  # Faz rollback caso ocorra erro
    finally:
        cursor.close()

    return redirect(url_for('criar_conta'))


class Receitas:
    def __init__(self, id_receita, valor, datadia, fonte, id_usuario):
        self.id_receita = id_receita
        self.valor = valor
        self.datadia = datadia
        self.fonte = fonte
        self.id_usuario = id_usuario


@app.route('/tabela_receitas')
def tabela_receitas():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado no sistema')
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']
    cursor = con.cursor()
    cursor.execute('SELECT id_receita, valor, datadia, fonte FROM receitas WHERE id_usuario = ?', (id_usuario,))
    receitas = cursor.fetchall()
    cursor.close()
    return render_template('tabela_receitas.html', receitas=receitas)


@app.route('/receitas')
def receitas():
    if 'id_usuario' not in session:
        flash('Voce precisa estar logado no sistema')
        return redirect(url_for('login'))
    return render_template('receitas.html', titulo='Nova Receita')


@app.route('/criar_receita', methods=['POST'])
def criar_receita():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado no sistema')
        return redirect(url_for('login'))

    valor = request.form['valor']
    datadia = request.form['datadia']
    fonte = request.form['fonte']
    id_usuario = session['id_usuario']

    cursor = con.cursor()
    try:
        # Verificar se a receita já existe para o mesmo usuário
        cursor.execute("SELECT 1 FROM receitas WHERE FONTE = ? AND DATADIA = ? AND ID_USUARIO = ?",
                       (fonte, datadia, id_usuario))
        if cursor.fetchone():
            flash("Erro: Receita já cadastrada.", "error")
            return redirect(url_for('receitas'))

        # Inserir o novo registro
        cursor.execute("INSERT INTO receitas (VALOR, DATADIA, FONTE, ID_USUARIO) VALUES (?, ?, ?, ?)",
                       (valor, datadia, fonte, id_usuario))
        con.commit()
        flash("Receita cadastrada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar receita: {str(e)}", "error")
        con.rollback()
    finally:
        cursor.close()

    return redirect(url_for('tabela_receitas'))


@app.route('/atualizar_receita')
def atuaizar_receita():
    if 'id_usuario' not in session:
        flash('Voce precisa estar logado no sistema')
        return redirect(url_for('login'))
    return render_template('editar_receita.html', titulo='Editar Receita')


@app.route('/editar_receita/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    cursor = con.cursor()  # Abre o cursor

    # Buscar o  específico para edição
    cursor.execute("SELECT ID_RECEITA, VALOR, DATADIA, FONTE FROM receitas WHERE ID_RECEITA = ?", (id,))
    receita = cursor.fetchone()

    if not receita:
        cursor.close()  # Fecha o cursor se o  não for encontrado
        flash("Receita não encontrado!", "error")
        return redirect(url_for('tabela_receitas'))  # Redireciona para a página principal se o  não for encontrado

    if request.method == 'POST':
        # Coleta os dados do formulário
        valor = request.form['valor']
        datadia = request.form['datadia']
        fonte = request.form['fonte']

        # Atualiza o  no banco de dados
        cursor.execute("UPDATE receitas SET VALOR = ?,  DATADIA = ?, FONTE = ? WHERE ID_RECEITA = ?",
                       (valor, datadia, fonte, id))
        con.commit()  # Salva as mudanças no banco de dados
        cursor.close()  # Fecha o cursor
        flash("Receita atualizada com sucesso!", "success")
        return redirect(url_for('tabela_receitas'))  # Redireciona para a página principal após a atualização

    cursor.close()  # Fecha o cursor ao final da função, se não for uma requisição POST
    return render_template('editar_receita.html', receita=receita, titulo='Editar Receita')


@app.route('/deletar_receita/<int:id>', methods=('POST',))
def deletar_receita(id):
    cursor = con.cursor()  # Abre o cursor

    try:
        cursor.execute('DELETE FROM receitas WHERE id_receita = ?', (id,))
        con.commit()  # Salva as alterações no banco de dados
        flash('Receita excluída com sucesso!', 'success')  # Mensagem de sucesso
    except Exception as e:
        con.rollback()  # Reverte as alterações em caso de erro
        flash('Erro ao excluir a receita.', 'error')  # Mensagem de erro
    finally:
        cursor.close()  # Fecha o cursor independentemente do resultado

    return redirect(url_for('tabela_receitas'))  # Redireciona para a página principal


class Despesas:
    def __init__(self, id_despesas, valor, datadia, fonte, id_usuario):
        self.id_despesas = id_despesas
        self.valor = valor
        self.datadia = datadia
        self.fonte = fonte
        self.id_usuario = id_usuario


@app.route('/tabela_despesas')
def tabela_despesas():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado no sistema')
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']
    cursor = con.cursor()
    cursor.execute('SELECT id_despesas, valor, datadia, fonte FROM despesas WHERE id_usuario = ?', (id_usuario,))
    despesas = cursor.fetchall()
    cursor.close()
    return render_template('tabela_despesas.html', despesas=despesas)


@app.route('/despesas')
def despesas():
    if 'id_usuario' not in session:
        flash('Voce precisa estar logado no sistema')
        return redirect(url_for('login'))
    return render_template('despesas.html', titulo='Nova Despesa')


@app.route('/criar_despesa', methods=['POST'])
def criar_despesa():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado no sistema')
        return redirect(url_for('login'))

    valor = request.form['valor']
    datadia = request.form['datadia']
    fonte = request.form['fonte']
    id_usuario = session['id_usuario']

    cursor = con.cursor()
    try:
        # Verificar se a despesa já existe para o mesmo usuário
        cursor.execute("SELECT 1 FROM despesas WHERE FONTE = ? AND DATADIA = ? AND ID_USUARIO = ?",
                       (fonte, datadia, id_usuario))
        if cursor.fetchone():
            flash("Erro: Despesa já cadastrada.", "error")
            return redirect(url_for('despesas'))

        # Inserir o novo registro
        cursor.execute("INSERT INTO despesas (VALOR, DATADIA, FONTE, ID_USUARIO) VALUES (?, ?, ?, ?)",
                       (valor, datadia, fonte, id_usuario))
        con.commit()
        flash("Despesa cadastrada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar despesa: {str(e)}", "error")
        con.rollback()
    finally:
        cursor.close()

    return redirect(url_for('tabela_despesas'))

@app.route('/atualizar_despesa')
def atuaizar_despesa():
    if 'id_usuario' not in session:
        flash('Voce precisa estar logado no sistema')
        return redirect(url_for('login'))
    return render_template('editar_despesa.html', titulo='Editar Despesa')


@app.route('/editar_despesa/<int:id>', methods=['GET', 'POST'])
def editar_despesa(id):
    if 'id_usuario' not in session:
        flash('Voce precisa estar logado no sistema')
        return redirect(url_for('login'))
    cursor = con.cursor()  # Abre o cursor

    # Buscar o  específico para edição
    cursor.execute("SELECT ID_DESPESAS, VALOR, DATADIA, FONTE FROM despesas WHERE ID_DESPESAS = ?", (id,))
    despesa = cursor.fetchone()

    if not despesa:
        cursor.close()  # Fecha o cursor se o  não for encontrado
        flash("Despesa não encontrada!", "error")
        return redirect(url_for('tabela_despesas'))  # Redireciona para a página principal se o  não for encontrado

    if request.method == 'POST':
        # Coleta os dados do formulário
        valor = request.form['valor']
        datadia = request.form['datadia']
        fonte = request.form['fonte']

        # Atualiza o  no banco de dados
        cursor.execute("UPDATE despesas SET VALOR = ?, DATADIA = ?, FONTE = ? WHERE ID_DESPESAS = ?",
                       (valor, datadia, fonte, id))
        con.commit()  # Salva as mudanças no banco de dados
        cursor.close()  # Fecha o cursor
        flash("Despesa atualizada com sucesso!", "success")
        return redirect(url_for('tabela_despesas'))  # Redireciona para a página principal após a atualização

    cursor.close()  # Fecha o cursor ao final da função, se não for uma requisição POST
    return render_template('editar_despesa.html', despesa=despesa, titulo='Editar Despesa')


@app.route('/deletar_despesa/<int:id>', methods=('POST',))
def deletar_despesa(id):
    cursor = con.cursor()  # Abre o cursor

    try:
        cursor.execute('DELETE FROM despesas WHERE id_despesas = ?', (id,))
        con.commit()  # Salva as alterações no banco de dados
        flash('Despesa excluída com sucesso!', 'success')  # Mensagem de sucesso
    except Exception as e:
        con.rollback()  # Reverte as alterações em caso de erro
        flash('Erro ao excluir a despesa.', 'error')  # Mensagem de erro
    finally:
        cursor.close()  # Fecha o cursor independentemente do resultado

    return redirect(url_for('tabela_despesas'))  # Redireciona para a página principal


@app.route('/controle')
def controle():
    cursor = con.cursor()

    id_usuario = session['id_usuario'] #usuário que acabou de logar

    cursor.execute("SELECT ID_DESPESAS, VALOR, DATADIA, FONTE FROM DESPESAS WHERE ID_USUARIO = ?", (id_usuario,))
    despesas = cursor.fetchall()
    cursor.execute("SELECT ID_RECEITA, VALOR, DATADIA, FONTE FROM RECEITAS WHERE ID_USUARIO = ?", (id_usuario,))
    receitas = cursor.fetchall()

    total_receita = 0
    total_despesa = 0

    if 'id_usuario' not in session:
        flash('Voce precisa estar logado no sistema')
        return redirect(url_for('index'))

    id_usuario = session['id_usuario']

    try:
        cursor.execute('SELECT coalesce(VALOR, 0) FROM RECEITA WHERE id_usuario = ?', (id_usuario,))
        receitas_db = cursor.fetchall()
        print(f'Valores das receitas: {receitas_db}')

        for row in receitas_db:
            total_receita += row[0]

        cursor.execute('SELECT coalesce(VALOR, 0) FROM DESPESAS WHERE id_usuario = ?', (id_usuario,))
        despesas_db = cursor.fetchall()
        print(f'Valores das despesas: {despesas_db}')

        for row in despesas_db:
            total_despesa += row[0]

        total_perda_lucro = total_receita - total_despesa

    except Exception as e:
        total_receita = 0
        total_despesa = 0
        total_perda_lucro = 0

    cursor.close()

    total_receita = f"{total_receita:.2f}"
    total_despesa = f"{total_despesa:.2f}"
    total_perda_lucro = f"{total_perda_lucro:.2f}"

    return render_template('controle.html', despesas=despesas, receitas=receitas, total_receita=total_receita, total_despesa=total_despesa, total_perda_lucro=total_perda_lucro)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/entrar', methods=['POST'])
def entrar():

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()
        try:
            cursor.execute("SELECT u.id_usuario, u.NOME, u.EMAIL, u.SENHA from usuario u WHERE u.EMAIL = ? AND u.SENHA = ?", (email, senha))
            usuario = cursor.fetchone()
        except Exception as e:
            flash('Erro gravissimo')
            return redirect(url_for('login'))
        finally:
            cursor.close()

        if usuario:
            session['id_usuario'] = usuario[0]
            session['nome'] = usuario[1]
            return redirect(url_for('controle'))
        else:
            flash('Email ou senha incorretos seu bocó')
    return render_template('criar_conta.html')

@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
