import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { listarAnimais } from '../servicos/api'
import './PaginaHistorico.css'

function IconeVoltar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

const ESPECIES = { gato: 'Gato', cachorro: 'Cachorro', coelho: 'Coelho', passaro: 'Pássaro' }
const EMOJIS   = { gato: '🐱', cachorro: '🐶', coelho: '🐰', passaro: '🐦' }

function formatarData(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-BR')
}

function calcularPermanencia(dataEntrada) {
  if (!dataEntrada) return '—'
  const entrada = new Date(dataEntrada)
  const hoje = new Date()
  const dias = Math.floor((hoje - entrada) / (1000 * 60 * 60 * 24))
  if (dias === 0) return 'Hoje'
  if (dias === 1) return '1 dia'
  return `${dias} dias`
}

export default function PaginaHistorico() {
  const navegar = useNavigate()

  const [animais, setAnimais]       = useState([])
  const [carregando, setCarregando] = useState(true)
  const [busca, setBusca]           = useState('')
  const [especie, setEspecie]       = useState('todos')
  const [status, setStatus]         = useState('todos')
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim]       = useState('')
  const [pagina, setPagina]         = useState(1)
  const POR_PAGINA = 10

  useEffect(() => {
    listarAnimais()
      .then(setAnimais)
      .catch(() => {})
      .finally(() => setCarregando(false))
  }, [])

  const filtrados = useMemo(() => {
    return animais.filter(a => {
      const textoBusca = busca.toLowerCase()
      const bateTexto = !busca
        || a.nome?.toLowerCase().includes(textoBusca)
        || a.tutor?.toLowerCase().includes(textoBusca)
        || a.veterinario?.toLowerCase().includes(textoBusca)

      const bateEspecie = especie === 'todos' || a.especie === especie
      const bateStatus  = status  === 'todos' || a.status_internacao === status

      const entrada = a.data_entrada ? new Date(a.data_entrada) : null
      const bateInicio = !dataInicio || (entrada && entrada >= new Date(dataInicio))
      const bateFim    = !dataFim    || (entrada && entrada <= new Date(dataFim + 'T23:59:59'))

      return bateTexto && bateEspecie && bateStatus && bateInicio && bateFim
    })
  }, [animais, busca, especie, status, dataInicio, dataFim])

  const totalPaginas = Math.max(1, Math.ceil(filtrados.length / POR_PAGINA))
  const paginaAtual  = Math.min(pagina, totalPaginas)
  const paginados    = filtrados.slice((paginaAtual - 1) * POR_PAGINA, paginaAtual * POR_PAGINA)

  function mudarFiltro(setter) {
    return (valor) => { setter(valor); setPagina(1) }
  }

  const internados = animais.filter(a => a.status_internacao === 'internado').length
  const altas      = animais.filter(a => a.status_internacao === 'alta').length

  return (
    <div className="pagina-historico">

      <header className="historico-cabecalho">
        <button className="botao-voltar-hist" onClick={() => navegar('/painel')}>
          <IconeVoltar /> Voltar ao Painel
        </button>
        <h1>Histórico de Animais</h1>
      </header>

      <main className="historico-conteudo">

        <div className="historico-resumo">
          <div className="resumo-card">
            <span>Total</span>
            <strong>{animais.length}</strong>
          </div>
          <div className="resumo-card resumo-card--internado">
            <span>Internados</span>
            <strong>{internados}</strong>
          </div>
          <div className="resumo-card resumo-card--alta">
            <span>Com Alta</span>
            <strong>{altas}</strong>
          </div>
        </div>

        <div className="historico-filtros">
          <input
            className="filtro-busca"
            type="text"
            placeholder="Buscar por nome, tutor ou veterinário..."
            value={busca}
            onChange={e => mudarFiltro(setBusca)(e.target.value)}
          />
          <select className="filtro-select" value={especie} onChange={e => mudarFiltro(setEspecie)(e.target.value)}>
            <option value="todos">Todas as espécies</option>
            <option value="gato">Gato</option>
            <option value="cachorro">Cachorro</option>
            <option value="coelho">Coelho</option>
            <option value="passaro">Pássaro</option>
          </select>
          <select className="filtro-select" value={status} onChange={e => mudarFiltro(setStatus)(e.target.value)}>
            <option value="todos">Todos os status</option>
            <option value="internado">Internado</option>
            <option value="alta">Com Alta</option>
          </select>
          <div className="filtro-periodo">
            <span className="filtro-periodo-label">Período de entrada</span>
            <div className="filtro-periodo-inputs">
              <input
                type="date"
                className="filtro-data"
                value={dataInicio}
                max={dataFim || undefined}
                onChange={e => mudarFiltro(setDataInicio)(e.target.value)}
              />
              <span className="filtro-periodo-sep">→</span>
              <input
                type="date"
                className={`filtro-data ${dataFim && dataInicio && dataFim < dataInicio ? 'filtro-data--erro' : ''}`}
                value={dataFim}
                min={dataInicio || undefined}
                onChange={e => mudarFiltro(setDataFim)(e.target.value)}
              />
              {(dataInicio || dataFim) && (
                <button className="filtro-limpar-data" onClick={() => { mudarFiltro(setDataInicio)(''); mudarFiltro(setDataFim)('') }}>
                  ×
                </button>
              )}
            </div>
            {dataFim && dataInicio && dataFim < dataInicio && (
              <span className="filtro-data-aviso">Data final menor que a inicial</span>
            )}
          </div>
        </div>

        {carregando ? (
          <p className="historico-estado">Carregando...</p>
        ) : filtrados.length === 0 ? (
          <p className="historico-estado">Nenhum animal encontrado.</p>
        ) : (
          <div className="historico-tabela-wrapper">
            <table className="historico-tabela">
              <thead>
                <tr>
                  <th>Animal</th>
                  <th>Raça</th>
                  <th>Tutor</th>
                  <th>Veterinário</th>
                  <th>Entrada</th>
                  <th>Permanência</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {paginados.map(a => (
                  <tr key={a.id_animal}>
                    <td>
                      <div className="animal-nome-cel">
                        <span className="animal-emoji">{EMOJIS[a.especie] ?? '🐾'}</span>
                        <div>
                          <strong>{a.nome}</strong>
                          <small>{ESPECIES[a.especie] ?? a.especie}</small>
                        </div>
                      </div>
                    </td>
                    <td>{a.raca ?? '—'}</td>
                    <td>{a.tutor ?? '—'}</td>
                    <td>{a.veterinario ?? '—'}</td>
                    <td>{formatarData(a.data_entrada)}</td>
                    <td>{calcularPermanencia(a.data_entrada)}</td>
                    <td>
                      <span className={`badge-status ${a.status_internacao === 'internado' ? 'badge-internado' : 'badge-alta'}`}>
                        {a.status_internacao === 'internado' ? 'Internado' : 'Alta'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="botao-ver-relatorio"
                        onClick={() => navegar(`/relatorio/${a.id_animal}`)}
                      >
                        Ver relatório
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPaginas > 1 && (
              <div className="historico-paginacao">
                <button
                  className="pag-btn"
                  onClick={() => setPagina(p => p - 1)}
                  disabled={paginaAtual === 1}
                >←</button>
                {Array.from({ length: totalPaginas }, (_, i) => i + 1).map(n => (
                  <button
                    key={n}
                    className={`pag-btn ${n === paginaAtual ? 'pag-btn--ativo' : ''}`}
                    onClick={() => setPagina(n)}
                  >{n}</button>
                ))}
                <button
                  className="pag-btn"
                  onClick={() => setPagina(p => p + 1)}
                  disabled={paginaAtual === totalPaginas}
                >→</button>
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  )
}
