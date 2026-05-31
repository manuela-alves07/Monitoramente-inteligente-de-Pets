import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { buscarAnimal, listarAlertasAnimal, listarEventos } from '../servicos/api'
import './PaginaRelatorio.css'

function formatarData(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR')
}


function formatarDataHora(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

const NOMES_ESPECIE = {
  gato: 'Gato', cachorro: 'Cachorro'
}

export default function PaginaRelatorio() {
  const { id } = useParams()
  const navegar = useNavigate()

  const [animal, setAnimal]         = useState(null)
  const [eventos, setEventos]       = useState([])
  const [alertasDB, setAlertasDB]   = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro]             = useState('')

  const observacoes = animal?.observacoes ?? ''
  const config = JSON.parse(localStorage.getItem('vetvision-config') || '{}')
  const nomeClinica = config.nomeClinica || 'VetVision'

  useEffect(() => {
    async function carregar() {
      try {
        const [a, e, al] = await Promise.all([
          buscarAnimal(id),
          listarEventos(id),
          listarAlertasAnimal(id),
        ])
        setAnimal(a)
        setEventos(e)
        setAlertasDB(al)
      } catch {
        setErro('Não foi possível carregar os dados do animal.')
      } finally {
        setCarregando(false)
      }
    }
    carregar()
  }, [id])

  if (carregando) return <div className="relatorio-loading">Carregando...</div>
  if (erro)       return <div className="relatorio-loading">{erro}</div>

  const refeicoes = eventos.filter(e => e.tipo_evento === 'refeicao')
  const agua      = eventos.filter(e => e.tipo_evento === 'agua')

  return (
    <div className="pagina-relatorio">

      <div className="relatorio-acoes nao-imprimivel">
        <button className="botao-voltar-rel" onClick={() => navegar(-1)}>
          ← Voltar
        </button>
        <button className="botao-imprimir" onClick={() => window.print()}>
          Imprimir / Salvar PDF
        </button>
      </div>

      <div className="relatorio-documento">

        <header className="relatorio-header">
          <div className="relatorio-clinica">
            <h1>{nomeClinica}</h1>
            <span>Relatório Clínico Veterinário</span>
          </div>
          <div className="relatorio-data-emissao">
            <span>Emitido em</span>
            <strong>{new Date().toLocaleDateString('pt-BR')}</strong>
          </div>
        </header>

        <hr className="relatorio-divisor" />

        <section className="relatorio-secao">
          <h2>Dados do Animal</h2>
          <div className="relatorio-grade">
            <div className="relatorio-campo">
              <span>Nome</span>
              <strong>{animal.nome}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Espécie</span>
              <strong>{NOMES_ESPECIE[animal.especie] ?? animal.especie}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Raça</span>
              <strong>{animal.raca ?? '—'}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Idade</span>
              <strong>{animal.idade ?? '—'}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Peso</span>
              <strong>{animal.peso ?? '—'}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Alergias</span>
              <strong>{animal.alergias ?? 'Nenhuma conhecida'}</strong>
            </div>
          </div>
        </section>

        <section className="relatorio-secao">
          <h2>Tutor</h2>
          <div className="relatorio-grade">
            <div className="relatorio-campo">
              <span>Nome</span>
              <strong>{animal.tutor ?? '—'}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Telefone</span>
              <strong>{animal.telefone ?? '—'}</strong>
            </div>
          </div>
        </section>

        <section className="relatorio-secao">
          <h2>Internação</h2>
          <div className="relatorio-grade">
            <div className="relatorio-campo">
              <span>Data de entrada</span>
              <strong>{formatarData(animal.data_entrada)}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Hora de entrada</span>
              <strong>{animal.data_entrada ? new Date(animal.data_entrada).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '—'}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Data de alta</span>
              <strong>{formatarData(animal.data_alta)}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Hora de alta</span>
              <strong>{animal.data_alta ? new Date(animal.data_alta).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '—'}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Status</span>
              <strong>{animal.status_internacao === 'internado' ? 'Internado' : 'Alta'}</strong>
            </div>
            <div className="relatorio-campo">
              <span>Veterinário responsável</span>
              <strong>{animal.veterinario ?? '—'}</strong>
            </div>
            <div className="relatorio-campo relatorio-campo--largo">
              <span>Motivo da internação</span>
              <strong>{animal.motivo ?? '—'}</strong>
            </div>
          </div>
        </section>

        {animal.data_alta && (
          <section className="relatorio-secao">
            <h2>Alta</h2>
            <div className="relatorio-grade">
              <div className="relatorio-campo">
                <span>Condição de saída</span>
                <strong>{{
                  curado: 'Curado',
                  estavel: 'Estável',
                  transferencia: 'Transferência',
                  a_pedido: 'A pedido do tutor',
                  obito: 'Óbito',
                }[animal.condicao_alta] ?? animal.condicao_alta ?? '—'}</strong>
              </div>
              <div className="relatorio-campo">
                <span>Data de retorno</span>
                <strong>{formatarData(animal.data_retorno)}</strong>
              </div>
              <div className="relatorio-campo relatorio-campo--largo">
                <span>Diagnóstico final</span>
                <strong>{animal.diagnostico_final ?? '—'}</strong>
              </div>
            </div>
            <div className="relatorio-campo relatorio-campo--bloco">
              <span>Medicamentos para casa</span>
              <p>{animal.medicamentos_alta ?? '—'}</p>
            </div>
            <div className="relatorio-campo relatorio-campo--bloco">
              <span>Instruções para o tutor</span>
              <p>{animal.instrucoes_alta ?? '—'}</p>
            </div>
          </section>
        )}

        <section className="relatorio-secao">
          <h2>Ficha Clínica</h2>
          <div className="relatorio-campo relatorio-campo--bloco">
            <span>Diagnóstico inicial</span>
            <p>{animal.diagnostico ?? '—'}</p>
          </div>
          <div className="relatorio-campo relatorio-campo--bloco">
            <span>Medicamentos em uso</span>
            <p>{animal.medicamentos ?? '—'}</p>
          </div>
        </section>

        <section className="relatorio-secao">
          <h2>Monitoramento de Alimentação</h2>
          {refeicoes.length === 0 ? (
            <p className="relatorio-vazio">Nenhuma refeição registrada</p>
          ) : (
            <table className="relatorio-tabela">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Data / Hora</th>
                  <th>Detectado por</th>
                </tr>
              </thead>
              <tbody>
                {refeicoes.map((r, i) => (
                  <tr key={r.id_evento}>
                    <td>{i + 1}</td>
                    <td>{formatarDataHora(r.data_hora)}</td>
                    <td>Monitoramento automático</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section className="relatorio-secao">
          <h2>Monitoramento de Hidratação</h2>
          {agua.length === 0 ? (
            <p className="relatorio-vazio">Nenhum registro de ingestão de água</p>
          ) : (
            <table className="relatorio-tabela">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Data / Hora</th>
                  <th>Detectado por</th>
                </tr>
              </thead>
              <tbody>
                {agua.map((r, i) => (
                  <tr key={r.id_evento}>
                    <td>{i + 1}</td>
                    <td>{formatarDataHora(r.data_hora)}</td>
                    <td>Monitoramento automático</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        {alertasDB.length > 0 && (
          <section className="relatorio-secao">
            <h2>Alertas Registrados</h2>
            <table className="relatorio-tabela">
              <thead>
                <tr><th>Data / Hora</th><th>Descrição</th><th>Status</th></tr>
              </thead>
              <tbody>
                {alertasDB.map(a => (
                  <tr key={a.id_alerta}>
                    <td>{formatarDataHora(a.criado_em)}</td>
                    <td>{a.descricao}</td>
                    <td>{a.status === 'aberto' ? 'Ativo' : 'Resolvido'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {observacoes && (
          <section className="relatorio-secao">
            <h2>Observações da Equipe</h2>
            <p className="relatorio-obs">{observacoes}</p>
          </section>
        )}

      </div>
    </div>
  )
}
