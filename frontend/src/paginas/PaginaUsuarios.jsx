import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { listarUsuarios, cadastrarUsuario, removerUsuario, atualizarSenha } from '../servicos/api'
import { isAdmin } from '../servicos/usuarios'
import './PaginaUsuarios.css'

function IconeVoltar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

export default function PaginaUsuarios() {
  const navegar = useNavigate()

  const [usuarios, setUsuarios]               = useState([])
  const [form, setForm]                       = useState({ nome: '', login: '', senha: '', role: 'user' })
  const [erro, setErro]                       = useState('')
  const [sucesso, setSucesso]                 = useState('')
  const [trocandoSenha, setTrocandoSenha]     = useState(null)
  const [novaSenha, setNovaSenha]             = useState('')
  const [salvando, setSalvando]               = useState(false)

  if (!isAdmin()) {
    return (
      <div className="pagina-usuarios">
        <p className="acesso-negado">Acesso restrito a administradores.</p>
      </div>
    )
  }

  useEffect(() => {
    listarUsuarios().then(setUsuarios).catch(() => setErro('Erro ao carregar usuários.'))
  }, [])

  function atualizar(campo, valor) {
    setForm(prev => ({ ...prev, [campo]: valor }))
    setErro('')
  }

  function mostrarSucesso(msg) {
    setSucesso(msg)
    setTimeout(() => setSucesso(''), 2000)
  }

  async function adicionar(e) {
    e.preventDefault()
    if (!form.nome.trim() || !form.login.trim() || !form.senha.trim()) {
      setErro('Preencha todos os campos.')
      return
    }
    setSalvando(true)
    try {
      await cadastrarUsuario({ nome: form.nome, login: form.login, senha: form.senha, role: form.role })
      const lista = await listarUsuarios()
      setUsuarios(lista)
      setForm({ nome: '', login: '', senha: '', role: 'user' })
      mostrarSucesso('Usuário cadastrado!')
    } catch (err) {
      setErro(err.message)
    } finally {
      setSalvando(false)
    }
  }

  async function remover(idUsuario) {
    try {
      await removerUsuario(idUsuario)
      setUsuarios(prev => prev.filter(u => u.id_usuario !== idUsuario))
    } catch {
      setErro('Erro ao remover usuário.')
    }
  }

  async function salvarNovaSenha(idUsuario) {
    if (!novaSenha.trim()) return
    try {
      await atualizarSenha(idUsuario, novaSenha.trim())
      setTrocandoSenha(null)
      setNovaSenha('')
      mostrarSucesso('Senha atualizada!')
    } catch {
      setErro('Erro ao atualizar senha.')
    }
  }

  return (
    <div className="pagina-usuarios">

      <header className="usuarios-cabecalho">
        <button className="botao-voltar-usuarios" onClick={() => navegar('/painel')}>
          <IconeVoltar /> Voltar ao Painel
        </button>
        <h1>Gerenciar Usuários</h1>
      </header>

      <main className="usuarios-conteudo">

        <div className="usuarios-secao">
          <h2>Usuários cadastrados</h2>
          <div className="lista-usuarios">
            {usuarios.map(u => (
              <div key={u.id_usuario} className="item-usuario">
                <div className="usuario-info">
                  <div className="usuario-avatar">{u.nome[0].toUpperCase()}</div>
                  <div>
                    <span className="usuario-nome">{u.nome}</span>
                    <span className="usuario-login">@{u.login}</span>
                  </div>
                  <span className={`usuario-role ${u.role === 'admin' ? 'role-admin' : 'role-user'}`}>
                    {u.role === 'admin' ? 'Admin' : 'Usuário'}
                  </span>
                </div>
                <div className="usuario-acoes">
                  {trocandoSenha === u.id_usuario ? (
                    <>
                      <input
                        className="input-nova-senha"
                        type="password"
                        placeholder="Nova senha"
                        value={novaSenha}
                        onChange={e => setNovaSenha(e.target.value)}
                      />
                      <button className="botao-confirmar" onClick={() => salvarNovaSenha(u.id_usuario)}>Salvar</button>
                      <button className="botao-cancelar-senha" onClick={() => setTrocandoSenha(null)}>Cancelar</button>
                    </>
                  ) : (
                    <>
                      <button className="botao-trocar-senha" onClick={() => { setTrocandoSenha(u.id_usuario); setNovaSenha('') }}>
                        Trocar senha
                      </button>
                      {u.login !== 'admin' && (
                        <button className="botao-remover-usuario" onClick={() => remover(u.id_usuario)}>
                          Remover
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="usuarios-secao">
          <h2>Novo usuário</h2>
          <form onSubmit={adicionar} className="form-usuario">
            <div className="form-usuario-grade">
              <div className="campo-usuario">
                <label>Nome completo</label>
                <input type="text" placeholder="Ex: Dra. Ana"
                  value={form.nome} onChange={e => atualizar('nome', e.target.value)} />
              </div>
              <div className="campo-usuario">
                <label>Usuário (login)</label>
                <input type="text" placeholder="Ex: ana.vet"
                  value={form.login} onChange={e => atualizar('login', e.target.value)} />
              </div>
              <div className="campo-usuario">
                <label>Senha</label>
                <input type="password" placeholder="••••••••"
                  value={form.senha} onChange={e => atualizar('senha', e.target.value)} />
              </div>
              <div className="campo-usuario">
                <label>Perfil</label>
                <select value={form.role} onChange={e => atualizar('role', e.target.value)}>
                  <option value="user">Usuário</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            {erro    && <p className="msg-erro">{erro}</p>}
            {sucesso && <p className="msg-sucesso">{sucesso}</p>}
            <button type="submit" className="botao-cadastrar-usuario" disabled={salvando}>
              {salvando ? 'Cadastrando...' : 'Cadastrar usuário'}
            </button>
          </form>
        </div>

      </main>
    </div>
  )
}
