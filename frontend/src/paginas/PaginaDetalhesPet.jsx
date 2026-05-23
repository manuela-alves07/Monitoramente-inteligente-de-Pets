import { useState, useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { analisarVideo } from '../servicos/api'
import './PaginaDetalhesPet.css'

function IconeVoltar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

function calcularTempoInternado(dataEntrada) {
  if (!dataEntrada) return '—'
  const entrada = new Date(dataEntrada + 'T00:00:00')
  const hoje    = new Date()
  const dias    = Math.floor((hoje - entrada) / (1000 * 60 * 60 * 24))
  if (dias === 0) return 'Hoje'
  if (dias === 1) return '1 dia'
  return `${dias} dias`
}

function formatarData(dataISO) {
  if (!dataISO) return '—'
  const [ano, mes, dia] = dataISO.split('-')
  return `${dia}/${mes}/${ano}`
}

export default function PaginaDetalhesPet() {
  const { state } = useLocation()
  const navegar = useNavigate()

  const baia      = state?.baia
  const chaveStorage = `obs-baia-${baia?.numero}`

  const [observacoes, setObservacoes]     = useState('')
  const [salvo, setSalvo]                 = useState(false)
  const [relatorioLocal, setRelatorioLocal] = useState(state?.relatorio ?? null)
  const [analisando, setAnalisando]       = useState(false)
  const [erroAnalise, setErroAnalise]     = useState('')
  const inputVideoRef = useRef(null)

  useEffect(() => {
    const salvas = localStorage.getItem(chaveStorage)
    if (salvas) setObservacoes(salvas)
  }, [chaveStorage])

  function salvarObservacoes() {
    localStorage.setItem(chaveStorage, observacoes)
    setSalvo(true)
    setTimeout(() => setSalvo(false), 2000)
  }

  async function enviarVideo(e) {
    const arquivo = e.target.files[0]
    if (!arquivo) return
    setAnalisando(true)
    setErroAnalise('')
    try {
      const resultado = await analisarVideo(arquivo)
      setRelatorioLocal(resultado)

      const baias = JSON.parse(localStorage.getItem('vetvision-baias') || '[]')
      const atualizadas = baias.map(b =>
        b.numero === baia.numero ? { ...b, temDados: true } : b
      )
      localStorage.setItem('vetvision-baias', JSON.stringify(atualizadas))
    } catch {
      setErroAnalise('Erro ao analisar o vídeo. Verifique se o servidor está rodando.')
    } finally {
      setAnalisando(false)
    }
  }

  if (!baia || !baia.pet) {
    return (
      <div className="pagina-detalhes">
        <header className="detalhes-cabecalho">
          <button className="botao-voltar" onClick={() => navegar('/painel')}>
            <IconeVoltar /> Voltar ao Painel
          </button>
        </header>
        <main className="detalhes-conteudo">
          <div className="detalhes-titulo">
            <span className="detalhes-emoji">🏠</span>
            <div>
              <h1>Baia {baia ? String(baia.numero).padStart(2, '0') : '—'}</h1>
              <span className="detalhes-subtitulo">Nenhum animal internado no momento</span>
            </div>
          </div>
          <div className="detalhes-secao">
            <h3>Observações</h3>
            <textarea className="detalhes-obs"
              placeholder="Adicione observações sobre esta baia..."
              value={observacoes} onChange={e => setObservacoes(e.target.value)} />
            <button className="botao-salvar" onClick={salvarObservacoes}>
              {salvo ? '✓ Salvo!' : 'Salvar observações'}
            </button>
          </div>
        </main>
      </div>
    )
  }

  const pet      = baia.pet
  const refeicoes = relatorioLocal?.refeicoes ?? []
  const ultimaAlimentacao = refeicoes.length > 0 ? refeicoes[refeicoes.length - 1].inicio : '—'
  const duracaoTotal = refeicoes.reduce((soma, r) => soma + r.duracao_s, 0)

  return (
    <div className="pagina-detalhes">

      <header className="detalhes-cabecalho">
        <button className="botao-voltar" onClick={() => navegar('/painel')}>
          <IconeVoltar /> Voltar ao Painel
        </button>
      </header>

      <main className="detalhes-conteudo">

        <div className="detalhes-titulo">
          <span className="detalhes-emoji">
            {{ gato: '🐱', cachorro: '🐶', coelho: '🐰', passaro: '🐦' }[pet.tipo] ?? '🐾'}
          </span>
          <div>
            <h1>{pet.nome}</h1>
            <span className="detalhes-subtitulo">
              Baia {String(baia.numero).padStart(2, '0')} · {{ gato: 'Gato', cachorro: 'Cachorro', coelho: 'Coelho', passaro: 'Pássaro' }[pet.tipo] ?? pet.tipo} · {pet.raca ?? '—'}
            </span>
          </div>
        </div>

        <div className="detalhes-cards">
          <div className="detalhe-card">
            <small>Idade</small>
            <strong>{pet.idade ?? '—'}</strong>
          </div>
          <div className="detalhe-card">
            <small>Peso</small>
            <strong>{pet.peso ?? '—'}</strong>
          </div>
          <div className="detalhe-card">
            <small>Internado há</small>
            <strong>{calcularTempoInternado(pet.dataEntrada)}</strong>
          </div>
          <div className="detalhe-card">
            <small>Refeições hoje</small>
            <strong>{refeicoes.length}</strong>
          </div>
        </div>

        <div className="detalhes-secao">
          <h3>Ficha Clínica</h3>
          <div className="detalhes-atividades">
            <div className="atividade-item">
              <span className="atividade-label">Motivo da internação</span>
              <span className="atividade-valor">{pet.motivo ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Diagnóstico inicial</span>
              <span className="atividade-valor">{pet.diagnostico ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Medicamentos em uso</span>
              <span className="atividade-valor">{pet.medicamentos ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Alergias</span>
              <span className="atividade-valor alerta-alergia">{pet.alergias ?? 'Nenhuma'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Veterinário responsável</span>
              <span className="atividade-valor">{pet.veterinario ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Tutor</span>
              <span className="atividade-valor">{pet.tutor ?? '—'}{pet.telefone && pet.telefone !== '—' ? ` · ${pet.telefone}` : ''}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Data de entrada</span>
              <span className="atividade-valor">{formatarData(pet.dataEntrada)}</span>
            </div>
          </div>
        </div>

        <div className="detalhes-secao">
          <div className="secao-topo">
            <h3>Monitoramento de Alimentação</h3>
            <input
              ref={inputVideoRef}
              type="file"
              accept="video/*"
              style={{ display: 'none' }}
              onChange={enviarVideo}
            />
            <button
              className="botao-analisar"
              onClick={() => inputVideoRef.current.click()}
              disabled={analisando}
            >
              {analisando ? 'Analisando...' : 'Analisar vídeo'}
            </button>
          </div>
          {erroAnalise && <p className="erro-analise">{erroAnalise}</p>}
          <div className="detalhes-atividades">
            <div className="atividade-item">
              <span className="atividade-label">Última alimentação detectada</span>
              <span className="atividade-valor">{ultimaAlimentacao}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Tempo total comendo hoje</span>
              <span className="atividade-valor">
                {duracaoTotal > 0
                  ? duracaoTotal >= 60 ? `${(duracaoTotal / 60).toFixed(1)} min` : `${duracaoTotal.toFixed(1)}s`
                  : '—'}
              </span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Última ingestão de água</span>
              <span className="atividade-valor">—</span>
            </div>
          </div>
        </div>

        {refeicoes.length > 0 && (
          <div className="detalhes-secao">
            <h3>Refeições detectadas hoje</h3>
            <table className="detalhes-tabela">
              <thead>
                <tr><th>Horário</th><th>Duração</th></tr>
              </thead>
              <tbody>
                {refeicoes.map((r, i) => (
                  <tr key={i}>
                    <td>{r.inicio}</td>
                    <td>{r.duracao_s}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="detalhes-secao">
          <h3>Observações da equipe</h3>
          <textarea className="detalhes-obs"
            placeholder="Adicione observações, evolução do quadro, procedimentos realizados..."
            value={observacoes} onChange={e => setObservacoes(e.target.value)} />
          <button className="botao-salvar" onClick={salvarObservacoes}>
            {salvo ? '✓ Salvo!' : 'Salvar observações'}
          </button>
        </div>

      </main>
    </div>
  )
}
