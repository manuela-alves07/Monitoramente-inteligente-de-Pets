import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { fecharAlerta, listarAlertas } from '../servicos/api'
import './PaginaAlertas.css'

function IconeVoltar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

const LABELS = {
  sem_alimentacao:       'Sem alimentação',
  sem_hidratacao:        'Sem hidratação',
  sem_refeicao_detectada: 'Nenhuma refeição detectada',
}


export default function PaginaAlertas() {
  const navegar = useNavigate()
  const [alertas, setAlertas]       = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro]             = useState('')

  useEffect(() => {
    listarAlertas()
      .then(setAlertas)
      .catch(() => setErro('Não foi possível carregar os alertas.'))
      .finally(() => setCarregando(false))
  }, [])

  async function fechar(idAlerta) {
    await fecharAlerta(idAlerta)
    setAlertas(prev => prev.filter(a => a.id_alerta !== idAlerta))
  }

  return (
    <div className="pagina-alertas">
      <header className="alertas-cabecalho">
        <button className="botao-voltar-alertas" onClick={() => navegar('/painel')}>
          <IconeVoltar /> Voltar ao Painel
        </button>
        <h1>Alertas Clínicos</h1>
      </header>

      <main className="alertas-conteudo">
        {carregando && <p className="alertas-estado">Carregando...</p>}
        {erro       && <p className="alertas-estado">{erro}</p>}
        {!carregando && !erro && alertas.length === 0 && (
          <p className="alertas-estado alertas-ok">Nenhum alerta aberto no momento.</p>
        )}

        {alertas.length > 0 && (
          <table className="alertas-tabela">
            <thead>
              <tr>
                <th>Animal</th>
                <th>Tipo</th>
                <th>Descrição</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {alertas.map(a => (
                <tr key={a.id_alerta} className={a.tipo_alerta === 'sem_refeicao_detectada' ? '' : 'linha-critica'}>
                  <td>{a.nome_animal ?? '—'}</td>
                  <td>{LABELS[a.tipo_alerta] ?? a.tipo_alerta}</td>
                  <td>{a.descricao}</td>
                  <td><button className="btn-fechar-alerta" onClick={() => fechar(a.id_alerta)}>Ciente</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </main>
    </div>
  )
}
