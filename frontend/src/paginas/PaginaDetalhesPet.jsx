import { useState, useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { analisarVideo, atualizarAnimal, buscarAnimal, buscarRelatorioAnimal, darBaixa, listarEventos, listarRelatoriosAnimal } from '../servicos/api'
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
  const entrada = new Date(dataEntrada)
  const hoje    = new Date()
  const dias    = Math.floor((hoje - entrada) / (1000 * 60 * 60 * 24))
  if (dias === 0) return 'Hoje'
  if (dias === 1) return '1 dia'
  return `${dias} dias`
}

function formatarData(dataISO) {
  if (!dataISO) return '—'
  return new Date(dataISO).toLocaleDateString('pt-BR')
}

export default function PaginaDetalhesPet() {
  const { state } = useLocation()
  const navegar = useNavigate()

  const baia         = state?.baia
  const chaveStorage = `obs-baia-${baia?.numero}`

  const [petCompleto, setPetCompleto]       = useState(null)
  const [observacoes, setObservacoes]       = useState('')
  const [salvo, setSalvo]                   = useState(false)
  const [relatorioLocal, setRelatorioLocal] = useState(state?.relatorio ?? null)
  const [analisando, setAnalisando]         = useState(false)
  const [erroAnalise, setErroAnalise]       = useState('')
  const [dandoBaixa, setDandoBaixa]         = useState(false)
  const [modalAlta, setModalAlta]           = useState(false)
  const [formAlta, setFormAlta]             = useState({
    condicao_alta: 'curado',
    diagnostico_final: '',
    medicamentos_alta: '',
    instrucoes_alta: '',
    data_retorno: '',
  })
  const [erroAlta, setErroAlta]             = useState('')
  const [eventosDB, setEventosDB]           = useState([])
  const [listaRelatorios, setListaRelatorios] = useState([])
  const [relatorioSelecionado, setRelatorioSelecionado] = useState(null)
  const [periodoFiltro, setPeriodoFiltro]   = useState('todos')
  const [modalEdicao, setModalEdicao]       = useState(false)
  const [formEdicao, setFormEdicao]         = useState({})
  const [salvandoEdicao, setSalvandoEdicao] = useState(false)
  const [erroEdicao, setErroEdicao]         = useState('')
  const inputVideoRef = useRef(null)

  useEffect(() => {
    const salvas = localStorage.getItem(chaveStorage)
    if (salvas) setObservacoes(salvas)
  }, [chaveStorage])

  useEffect(() => {
    if (baia?.pet?.id) {
      buscarAnimal(baia.pet.id).then(setPetCompleto).catch(() => {})
      listarEventos(baia.pet.id).then(setEventosDB).catch(() => {})

      const chaveCache = `relatorio-animal-${baia.pet.id}`
      if (!relatorioLocal) {
        const cache = localStorage.getItem(chaveCache)
        if (cache) {
          try { setRelatorioLocal(JSON.parse(cache)) } catch { /* cache corrompido */ }
        }
      }

      listarRelatoriosAnimal(baia.pet.id)
        .then(lista => {
          setListaRelatorios(lista)
          if (lista.length > 0 && !relatorioSelecionado) {
            setRelatorioSelecionado(lista[0].id_relatorio)
          }
        })
        .catch(() => {})
    }
  }, [baia?.pet?.id])

  useEffect(() => {
    if (!baia?.pet?.id) return
    if (!relatorioSelecionado) {
      buscarRelatorioAnimal(baia.pet.id)
        .then(r => r && setRelatorioLocal(r))
        .catch(() => {})
      return
    }
    buscarRelatorioAnimal(baia.pet.id, { id: relatorioSelecionado })
      .then(r => setRelatorioLocal(r))
      .catch(() => {})
  }, [baia?.pet?.id, relatorioSelecionado])

  function salvarObservacoes() {
    localStorage.setItem(chaveStorage, observacoes)
    setSalvo(true)
    setTimeout(() => setSalvo(false), 2000)
  }

  function abrirEdicao() {
    setFormEdicao({
      nome:         pet.nome ?? '',
      especie:      pet.especie ?? 'gato',
      raca:         pet.raca ?? '',
      tutor:        pet.tutor ?? '',
      telefone:     pet.telefone ?? '',
      idade:        pet.idade ?? '',
      peso:         pet.peso ?? '',
      motivo:       pet.motivo ?? '',
      diagnostico:  pet.diagnostico ?? '',
      medicamentos: pet.medicamentos ?? '',
      alergias:     pet.alergias ?? '',
      veterinario:  pet.veterinario ?? '',
    })
    setErroEdicao('')
    setModalEdicao(true)
  }

  async function salvarEdicao() {
    if (!formEdicao.nome?.trim() || !formEdicao.tutor?.trim()) {
      setErroEdicao('Nome e tutor são obrigatórios.')
      return
    }
    setSalvandoEdicao(true)
    try {
      await atualizarAnimal(pet.id, formEdicao)
      setModalEdicao(false)
      navegar('/painel')
    } catch {
      setErroEdicao('Erro ao salvar. Tente novamente.')
      setSalvandoEdicao(false)
    }
  }

  function abrirModalAlta() {
    setModalAlta(true)
  }

  async function confirmarAlta() {
    if (!formAlta.diagnostico_final.trim() || !formAlta.medicamentos_alta.trim() || !formAlta.instrucoes_alta.trim()) {
      setErroAlta('Preencha diagnóstico final, medicamentos e instruções antes de confirmar.')
      return
    }
    setErroAlta('')
    setDandoBaixa(true)
    try {
      await darBaixa(pet.id, {
        condicao_alta: formAlta.condicao_alta,
        diagnostico_final: formAlta.diagnostico_final || null,
        medicamentos_alta: formAlta.medicamentos_alta || null,
        instrucoes_alta: formAlta.instrucoes_alta || null,
        data_retorno: formAlta.data_retorno || null,
      })
      navegar('/painel')
    } catch {
      alert('Erro ao dar alta. Verifique se o servidor está rodando.')
      setDandoBaixa(false)
      setModalAlta(false)
    }
  }

  async function enviarVideo(e) {
    const arquivo = e.target.files[0]
    if (!arquivo) return
    setAnalisando(true)
    setErroAnalise('')
    try {
      const resultado = await analisarVideo(arquivo, baia?.pet?.id)
      setRelatorioLocal(resultado)
      if (baia?.pet?.id) {
        localStorage.setItem(`relatorio-animal-${baia.pet.id}`, JSON.stringify(resultado))
        listarRelatoriosAnimal(baia.pet.id)
          .then(lista => {
            setListaRelatorios(lista)
            if (lista.length > 0) setRelatorioSelecionado(lista[0].id_relatorio)
          })
          .catch(() => {})
      }
    } catch (err) {
      setErroAnalise(err.message || 'Erro ao analisar o vídeo.')
    } finally {
      setAnalisando(false)
      e.target.value = ''
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
  const dados    = petCompleto ?? pet

  function periodoDoHorario(horario) {
    if (!horario) return null
    const hora = Number(horario.slice(0, 2))
    if (hora >= 6  && hora < 12) return 'manha'
    if (hora >= 12 && hora < 18) return 'tarde'
    return 'noite'
  }

  const refeicoesTodas = relatorioLocal?.refeicoes ?? []
  const refeicoes = periodoFiltro === 'todos'
    ? refeicoesTodas
    : refeicoesTodas.filter(r => periodoDoHorario(r.inicio) === periodoFiltro)

  const ultimaAlimentacao = refeicoes.length > 0 ? refeicoes[refeicoes.length - 1].inicio : '—'
  const duracaoTotal = refeicoes.reduce((soma, r) => soma + r.duracao_s, 0)

  const eventosAgua = eventosDB.filter(e => e.tipo_evento === 'agua')
  const ultimaAgua  = eventosAgua.length > 0
    ? new Date(eventosAgua[0].data_hora).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    : '—'

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
            {{ gato: '🐱', cachorro: '🐶', coelho: '🐰', passaro: '🐦' }[dados.tipo ?? dados.especie] ?? '🐾'}
          </span>
          <div>
            <h1>{dados.nome}</h1>
            <span className="detalhes-subtitulo">
              Baia {baia.numero} · {{ gato: 'Gato', cachorro: 'Cachorro', coelho: 'Coelho', passaro: 'Pássaro' }[dados.tipo ?? dados.especie] ?? dados.especie} · {dados.raca ?? '—'}
            </span>
          </div>
        </div>

        <div className="detalhes-cards">
          <div className="detalhe-card">
            <small>Idade</small>
            <strong>{dados.idade ?? '—'}</strong>
          </div>
          <div className="detalhe-card">
            <small>Peso</small>
            <strong>{dados.peso ?? '—'}</strong>
          </div>
          <div className="detalhe-card">
            <small>Internado há</small>
            <strong>{calcularTempoInternado(dados.dataEntrada ?? dados.data_entrada)}</strong>
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
              <span className="atividade-valor">{dados.motivo ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Diagnóstico inicial</span>
              <span className="atividade-valor">{dados.diagnostico ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Medicamentos em uso</span>
              <span className="atividade-valor">{dados.medicamentos ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Alergias</span>
              <span className="atividade-valor alerta-alergia">{dados.alergias ?? 'Nenhuma'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Veterinário responsável</span>
              <span className="atividade-valor">{dados.veterinario ?? '—'}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Tutor</span>
              <span className="atividade-valor">{dados.tutor ?? '—'}{dados.telefone ? ` · ${dados.telefone}` : ''}</span>
            </div>
            <div className="atividade-item">
              <span className="atividade-label">Data de entrada</span>
              <span className="atividade-valor">{formatarData(dados.dataEntrada ?? dados.data_entrada)}</span>
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

          {listaRelatorios.length > 0 && (
            <div className="filtro-data-relatorio">
              <label htmlFor="filtro-relatorio">Análise:</label>
              <select
                id="filtro-relatorio"
                value={relatorioSelecionado ?? ''}
                onChange={e => setRelatorioSelecionado(Number(e.target.value))}
              >
                {listaRelatorios.map(item => {
                  const hora = item.gerado_em?.slice(11, 16) ?? ''
                  return (
                    <option key={item.id_relatorio} value={item.id_relatorio}>
                      {formatarData(item.data)} {hora} · {item.refeicoes_confirmadas} refeição(ões)
                    </option>
                  )
                })}
              </select>

              <label htmlFor="filtro-periodo">Período:</label>
              <select
                id="filtro-periodo"
                value={periodoFiltro}
                onChange={e => setPeriodoFiltro(e.target.value)}
              >
                <option value="todos">Todos ({refeicoesTodas.length})</option>
                <option value="manha">Manhã 06h–12h ({refeicoesTodas.filter(r => periodoDoHorario(r.inicio) === 'manha').length})</option>
                <option value="tarde">Tarde 12h–18h ({refeicoesTodas.filter(r => periodoDoHorario(r.inicio) === 'tarde').length})</option>
                <option value="noite">Noite 18h–06h ({refeicoesTodas.filter(r => periodoDoHorario(r.inicio) === 'noite').length})</option>
              </select>
            </div>
          )}

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
              <span className="atividade-valor">{ultimaAgua}</span>
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

        <div className="detalhes-acoes-alta">
          <button className="botao-editar" onClick={abrirEdicao}>
            Editar dados
          </button>
          <button className="botao-relatorio" onClick={() => navegar(`/relatorio/${pet.id}`)}>
            Gerar Relatório
          </button>
          <button className="botao-dar-alta" onClick={abrirModalAlta} disabled={dandoBaixa}>
            {dandoBaixa ? 'Processando...' : 'Dar Alta ao Animal'}
          </button>
        </div>

      </main>

      {modalAlta && (
        <div className="modal-overlay" onClick={() => setModalAlta(false)}>
          <div className="modal-alta" onClick={e => e.stopPropagation()}>
            <h2>Alta de {pet.nome}</h2>

            <label className="modal-label">
              Condição de saída
              <select
                className="modal-input"
                value={formAlta.condicao_alta}
                onChange={e => setFormAlta(f => ({ ...f, condicao_alta: e.target.value }))}
              >
                <option value="curado">Curado</option>
                <option value="estavel">Estável</option>
                <option value="transferencia">Transferência</option>
                <option value="a_pedido">A pedido do tutor</option>
                <option value="obito">Óbito</option>
              </select>
            </label>

            <label className="modal-label">
              Diagnóstico final
              <textarea
                className="modal-input modal-textarea"
                placeholder="Diagnóstico ao receber alta..."
                value={formAlta.diagnostico_final}
                onChange={e => setFormAlta(f => ({ ...f, diagnostico_final: e.target.value }))}
              />
            </label>

            <label className="modal-label">
              Medicamentos para casa
              <textarea
                className="modal-input modal-textarea"
                placeholder="Ex: Amoxicilina 250mg, 2x ao dia por 7 dias..."
                value={formAlta.medicamentos_alta}
                onChange={e => setFormAlta(f => ({ ...f, medicamentos_alta: e.target.value }))}
              />
            </label>

            <label className="modal-label">
              Instruções para o tutor
              <textarea
                className="modal-input modal-textarea"
                placeholder="Cuidados em casa, restrições, alimentação..."
                value={formAlta.instrucoes_alta}
                onChange={e => setFormAlta(f => ({ ...f, instrucoes_alta: e.target.value }))}
              />
            </label>

            <label className="modal-label">
              Data de retorno (opcional)
              <input
                type="date"
                className="modal-input"
                value={formAlta.data_retorno}
                onChange={e => setFormAlta(f => ({ ...f, data_retorno: e.target.value }))}
              />
            </label>

            {erroAlta && <span className="modal-erro">{erroAlta}</span>}
            <div className="modal-acoes">
              <button className="modal-btn-cancelar" onClick={() => setModalAlta(false)}>
                Cancelar
              </button>
              <button className="modal-btn-confirmar" onClick={confirmarAlta} disabled={dandoBaixa}>
                {dandoBaixa ? 'Processando...' : 'Confirmar Alta'}
              </button>
            </div>
          </div>
        </div>
      )}

      {modalEdicao && (
        <div className="modal-overlay" onClick={() => setModalEdicao(false)}>
          <div className="modal-alta" onClick={e => e.stopPropagation()}>
            <h2>Editar dados de {pet.nome}</h2>

            <div className="modal-grade">
              <label className="modal-label">
                Nome
                <input className="modal-input" value={formEdicao.nome}
                  onChange={e => setFormEdicao(f => ({ ...f, nome: e.target.value }))} />
              </label>
              <label className="modal-label">
                Espécie
                <select className="modal-input" value={formEdicao.especie}
                  onChange={e => setFormEdicao(f => ({ ...f, especie: e.target.value }))}>
                  <option value="gato">Gato</option>
                  <option value="cachorro">Cachorro</option>
                  <option value="coelho">Coelho</option>
                  <option value="passaro">Pássaro</option>
                </select>
              </label>
              <label className="modal-label">
                Raça
                <input className="modal-input" value={formEdicao.raca}
                  onChange={e => setFormEdicao(f => ({ ...f, raca: e.target.value }))} />
              </label>
              <label className="modal-label">
                Idade
                <input className="modal-input" value={formEdicao.idade}
                  onChange={e => setFormEdicao(f => ({ ...f, idade: e.target.value }))} />
              </label>
              <label className="modal-label">
                Peso
                <input className="modal-input" value={formEdicao.peso}
                  onChange={e => setFormEdicao(f => ({ ...f, peso: e.target.value }))} />
              </label>
              <label className="modal-label">
                Tutor
                <input className="modal-input" value={formEdicao.tutor}
                  onChange={e => setFormEdicao(f => ({ ...f, tutor: e.target.value }))} />
              </label>
              <label className="modal-label">
                Telefone
                <input className="modal-input" value={formEdicao.telefone}
                  onChange={e => setFormEdicao(f => ({ ...f, telefone: e.target.value }))} />
              </label>
              <label className="modal-label">
                Veterinário
                <input className="modal-input" value={formEdicao.veterinario}
                  onChange={e => setFormEdicao(f => ({ ...f, veterinario: e.target.value }))} />
              </label>
            </div>

            <label className="modal-label">
              Motivo da internação
              <textarea className="modal-input modal-textarea" value={formEdicao.motivo}
                onChange={e => setFormEdicao(f => ({ ...f, motivo: e.target.value }))} />
            </label>
            <label className="modal-label">
              Diagnóstico inicial
              <textarea className="modal-input modal-textarea" value={formEdicao.diagnostico}
                onChange={e => setFormEdicao(f => ({ ...f, diagnostico: e.target.value }))} />
            </label>
            <label className="modal-label">
              Medicamentos em uso
              <textarea className="modal-input modal-textarea" value={formEdicao.medicamentos}
                onChange={e => setFormEdicao(f => ({ ...f, medicamentos: e.target.value }))} />
            </label>
            <label className="modal-label">
              Alergias
              <input className="modal-input" value={formEdicao.alergias}
                onChange={e => setFormEdicao(f => ({ ...f, alergias: e.target.value }))} />
            </label>

            {erroEdicao && <span className="modal-erro">{erroEdicao}</span>}
            <div className="modal-acoes">
              <button className="modal-btn-cancelar" onClick={() => setModalEdicao(false)}>Cancelar</button>
              <button className="modal-btn-salvar" onClick={salvarEdicao} disabled={salvandoEdicao}>
                {salvandoEdicao ? 'Salvando...' : 'Salvar alterações'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
