import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { trocarMinhaSenha } from '../servicos/api'
import './PaginaPerfil.css'

function IconeVoltar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

export default function PaginaPerfil() {
  const navegar = useNavigate()

  const nome  = localStorage.getItem('vetvision-usuario') ?? '—'
  const login = localStorage.getItem('vetvision-login')   ?? '—'
  const role  = localStorage.getItem('vetvision-role')    ?? 'user'

  const [senhaAtual, setSenhaAtual] = useState('')
  const [novaSenha, setNovaSenha]   = useState('')
  const [confirmar, setConfirmar]   = useState('')
  const [salvando, setSalvando]     = useState(false)
  const [erro, setErro]             = useState('')
  const [sucesso, setSucesso]       = useState('')

  async function trocarSenha(e) {
    e.preventDefault()
    setErro('')
    setSucesso('')

    if (!senhaAtual || !novaSenha || !confirmar) {
      setErro('Preencha todos os campos.')
      return
    }
    if (novaSenha !== confirmar) {
      setErro('A nova senha e a confirmação não coincidem.')
      return
    }
    if (novaSenha.length < 4) {
      setErro('A nova senha deve ter pelo menos 4 caracteres.')
      return
    }

    setSalvando(true)
    try {
      await trocarMinhaSenha(login, senhaAtual, novaSenha)
      setSenhaAtual('')
      setNovaSenha('')
      setConfirmar('')
      setSucesso('Senha alterada com sucesso!')
    } catch (err) {
      setErro(err.message)
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="pagina-perfil">
      <header className="perfil-cabecalho">
        <button className="botao-voltar-perfil" onClick={() => navegar('/painel')}>
          <IconeVoltar /> Voltar ao Painel
        </button>
        <h1>Meu Perfil</h1>
      </header>

      <main className="perfil-conteudo">

        <section className="perfil-secao">
          <div className="perfil-avatar">{nome[0]?.toUpperCase()}</div>
          <div className="perfil-info">
            <div className="perfil-campo">
              <span>Nome</span>
              <strong>{nome}</strong>
            </div>
            <div className="perfil-campo">
              <span>Usuário</span>
              <strong>{login}</strong>
            </div>
            <div className="perfil-campo">
              <span>Perfil</span>
              <strong>{role === 'admin' ? 'Administrador' : 'Veterinário'}</strong>
            </div>
          </div>
        </section>

        <section className="perfil-secao">
          <h2>Alterar senha</h2>
          <form onSubmit={trocarSenha} className="perfil-form">
            <label className="perfil-label">
              Senha atual
              <input
                type="password"
                className="perfil-input"
                value={senhaAtual}
                onChange={e => setSenhaAtual(e.target.value)}
                placeholder="••••••••"
              />
            </label>
            <label className="perfil-label">
              Nova senha
              <input
                type="password"
                className="perfil-input"
                value={novaSenha}
                onChange={e => setNovaSenha(e.target.value)}
                placeholder="••••••••"
              />
            </label>
            <label className="perfil-label">
              Confirmar nova senha
              <input
                type="password"
                className="perfil-input"
                value={confirmar}
                onChange={e => setConfirmar(e.target.value)}
                placeholder="••••••••"
              />
            </label>
            {erro    && <p className="perfil-erro">{erro}</p>}
            {sucesso && <p className="perfil-sucesso">{sucesso}</p>}
            <button type="submit" className="perfil-botao" disabled={salvando}>
              {salvando ? 'Salvando...' : 'Alterar senha'}
            </button>
          </form>
        </section>

      </main>
    </div>
  )
}
