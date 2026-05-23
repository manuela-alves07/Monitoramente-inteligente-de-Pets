import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PainelIlustracao from '../componentes/PainelIlustracao'
import './PaginaLogin.css'

function IconeUsuario() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  )
}

function IconeCadeado() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  )
}

function IconeOlhoAberto() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function IconeOlhoFechado() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  )
}

function LogoVetVision() {
  return (
    <svg width="54" height="54" viewBox="0 0 54 54" fill="none">
      <rect width="54" height="54" rx="14" fill="rgba(0,212,200,0.15)" />
      <ellipse cx="27" cy="33" rx="9" ry="7.5" fill="#00d4c8" />
      <ellipse cx="14.5" cy="27" rx="3.5" ry="4.5"
        transform="rotate(-15 14.5 27)" fill="#00d4c8" />
      <ellipse cx="20.5" cy="22" rx="3.2" ry="4.2"
        transform="rotate(-5 20.5 22)" fill="#00d4c8" />
      <ellipse cx="33.5" cy="22" rx="3.2" ry="4.2"
        transform="rotate(5 33.5 22)" fill="#00d4c8" />
      <ellipse cx="39.5" cy="27" rx="3.5" ry="4.5"
        transform="rotate(15 39.5 27)" fill="#00d4c8" />
    </svg>
  )
}

export default function PaginaLogin() {
  const navegar = useNavigate()

  const [usuario, setUsuario]           = useState('')
  const [senha, setSenha]               = useState('')
  const [lembrarMe, setLembrarMe]       = useState(true)
  const [mostrarSenha, setMostrarSenha] = useState(false)

  function handleEnviarFormulario(evento) {
    evento.preventDefault()
    if (usuario.trim()) localStorage.setItem('vetvision-usuario', usuario.trim())
    navegar('/painel')
  }

  return (
    <div className="pagina-login">

      <div className="lado-esquerdo">
        <PainelIlustracao />
      </div>

      <div className="lado-direito">

        <div className="marca">
          <LogoVetVision />
          <span className="nome-marca">VetVision</span>
        </div>

        <h1 className="titulo">Bem-vindo ao VetVision</h1>
        <p className="subtitulo">Monitoramento Inteligente para Pequenos Animais</p>

        <form onSubmit={handleEnviarFormulario} className="formulario">

          <div className="campo">
            <label htmlFor="usuario">E-mail ou Usuário</label>
            <div className="campo-icone">
              <span className="icone-esquerda"><IconeUsuario /></span>
              <input
                id="usuario"
                type="text"
                placeholder="email@gmail.com"
                value={usuario}
                onChange={(e) => setUsuario(e.target.value)}
                autoComplete="username"
              />
            </div>
          </div>

          <div className="campo">
            <label htmlFor="senha">Senha</label>
            <div className="campo-icone">
              <span className="icone-esquerda"><IconeCadeado /></span>
              <input
                id="senha"
                type={mostrarSenha ? 'text' : 'password'}
                placeholder="••••••••"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="botao-olho"
                onClick={() => setMostrarSenha(!mostrarSenha)}
                title={mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'}
              >
                {mostrarSenha ? <IconeOlhoFechado /> : <IconeOlhoAberto />}
              </button>
            </div>
          </div>

          <div className="linha-opcoes">
            <label className="toggle-lembrar">
              <input
                type="checkbox"
                checked={lembrarMe}
                onChange={(e) => setLembrarMe(e.target.checked)}
              />
              <span className="trilho-toggle" />
              <span className="texto-lembrar">Lembrar-me</span>
            </label>
            <a href="/esqueci-senha" className="link-esqueceu">
              Esqueci minha Senha?
            </a>
          </div>

          <button type="submit" className="botao-entrar">
            Acessar o Painel
          </button>

          <p className="texto-cadastro">
            Não tem uma conta?{' '}
            <a href="/solicitar-acesso" className="link-cadastro">
              Solicite acesso à sua clínica.
            </a>
          </p>

        </form>
      </div>

    </div>
  )
}
