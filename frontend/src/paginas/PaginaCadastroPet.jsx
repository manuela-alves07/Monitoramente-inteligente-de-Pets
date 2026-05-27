import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { cadastrarAnimal, listarBaias } from '../servicos/api'
import './PaginaCadastroPet.css'

function IconeVoltar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

function mascaraTelefone(valor) {
  const nums = valor.replace(/\D/g, '').slice(0, 11)
  if (nums.length <= 2)  return `(${nums}`
  if (nums.length <= 6)  return `(${nums.slice(0,2)}) ${nums.slice(2)}`
  if (nums.length <= 10) return `(${nums.slice(0,2)}) ${nums.slice(2,6)}-${nums.slice(6)}`
  return `(${nums.slice(0,2)}) ${nums.slice(2,7)}-${nums.slice(7)}`
}

function validarTelefone(valor) {
  return /^\(\d{2}\) \d{4,5}-\d{4}$/.test(valor.trim())
}

export default function PaginaCadastroPet() {
  const navegar = useNavigate()

  const hoje = new Date().toISOString().split('T')[0]

  const [baiasVazias, setBaiasVazias] = useState([])
  const [erroCadastro, setErroCadastro] = useState('')
  const [salvando, setSalvando] = useState(false)

  const [form, setForm] = useState({
    nome: '',
    tipo: 'gato',
    raca: '',
    idade: '',
    peso: '',
    tutor: '',
    telefone: '',
    baia: '',
    motivo: '',
    diagnostico: '',
    medicamentos: '',
    alergias: '',
    veterinario: '',
    dataEntrada: hoje,
  })

  const [erros, setErros] = useState({})

  useEffect(() => {
    async function carregar() {
      try {
        const lista = await listarBaias()
        const livres = lista.filter(b => !b.id_animal || b.status_internacao !== 'internado')
        setBaiasVazias(livres)
        if (livres[0]) setForm(prev => ({ ...prev, baia: String(livres[0].id_baia) }))
      } catch (erro) {
        setErroCadastro('Não foi possível carregar as baias do servidor.')
      }
    }
    carregar()
  }, [])

  function atualizar(campo, valor) {
    setForm(prev => ({ ...prev, [campo]: valor }))
    if (erros[campo]) setErros(prev => ({ ...prev, [campo]: '' }))
  }

  function atualizarTelefone(valor) {
    atualizar('telefone', mascaraTelefone(valor))
  }

  function validar() {
    const novosErros = {}

    if (!form.nome.trim())
      novosErros.nome = 'Nome do animal é obrigatório.'
    if (!form.tutor.trim())
      novosErros.tutor = 'Nome do tutor é obrigatório.'
    if (!form.telefone.trim())
      novosErros.telefone = 'Telefone é obrigatório.'
    else if (!validarTelefone(form.telefone))
      novosErros.telefone = 'Formato inválido. Use (XX) XXXXX-XXXX.'
    if (!form.baia)
      novosErros.baia = 'Selecione uma baia.'
    if (!form.motivo.trim())
      novosErros.motivo = 'Motivo da internação é obrigatório.'
    if (!form.veterinario.trim())
      novosErros.veterinario = 'Veterinário responsável é obrigatório.'

    setErros(novosErros)
    return Object.keys(novosErros).length === 0
  }

  async function salvar(e) {
    e.preventDefault()
    if (!validar()) return

    setErroCadastro('')
    setSalvando(true)
    try {
      await cadastrarAnimal({
        nome:         form.nome.trim(),
        especie:      form.tipo,
        raca:         form.raca.trim() || null,
        tutor:        form.tutor.trim(),
        id_baia:      Number(form.baia),
        telefone:     form.telefone.trim() || null,
        idade:        form.idade.trim() || null,
        peso:         form.peso.trim() || null,
        motivo:       form.motivo.trim() || null,
        diagnostico:  form.diagnostico.trim() || null,
        medicamentos: form.medicamentos.trim() || null,
        alergias:     form.alergias.trim() || null,
        veterinario:  form.veterinario.trim() || null,
      })
      navegar('/painel')
    } catch (erro) {
      setErroCadastro(erro.message || 'Erro ao cadastrar.')
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="pagina-cadastro">

      <header className="cadastro-cabecalho">
        <button className="botao-voltar-cad" onClick={() => navegar('/painel')}>
          <IconeVoltar /> Voltar ao Painel
        </button>
        <h1>Cadastrar Animal</h1>
      </header>

      <main className="cadastro-conteudo">
        <form onSubmit={salvar} noValidate>

          <div className="cadastro-secao">
            <h2>Dados do Animal</h2>
            <div className="cadastro-grade">
              <div className={`campo campo--largo ${erros.nome ? 'campo--erro' : ''}`}>
                <label>Nome <span className="obrigatorio">*</span></label>
                <input type="text" placeholder="Ex: Luna"
                  value={form.nome} onChange={e => atualizar('nome', e.target.value)} />
                {erros.nome && <span className="mensagem-erro">{erros.nome}</span>}
              </div>
              <div className="campo">
                <label>Espécie</label>
                <select value={form.tipo} onChange={e => atualizar('tipo', e.target.value)}>
                  <option value="gato">Gato</option>
                  <option value="cachorro">Cachorro</option>
                  <option value="coelho">Coelho</option>
                  <option value="passaro">Pássaro</option>
                </select>
              </div>
              <div className="campo">
                <label>Raça</label>
                <input type="text" placeholder="Ex: Persa"
                  value={form.raca} onChange={e => atualizar('raca', e.target.value)} />
              </div>
              <div className="campo">
                <label>Idade</label>
                <input type="text" placeholder="Ex: 3 anos"
                  value={form.idade} onChange={e => atualizar('idade', e.target.value)} />
              </div>
              <div className="campo">
                <label>Peso</label>
                <input type="text" placeholder="Ex: 4.2 kg"
                  value={form.peso} onChange={e => atualizar('peso', e.target.value)} />
              </div>
            </div>
          </div>

          <div className="cadastro-secao">
            <h2>Dados do Tutor</h2>
            <div className="cadastro-grade">
              <div className={`campo campo--largo ${erros.tutor ? 'campo--erro' : ''}`}>
                <label>Nome do tutor <span className="obrigatorio">*</span></label>
                <input type="text" placeholder="Ex: Maria Silva"
                  value={form.tutor} onChange={e => atualizar('tutor', e.target.value)} />
                {erros.tutor && <span className="mensagem-erro">{erros.tutor}</span>}
              </div>
              <div className={`campo ${erros.telefone ? 'campo--erro' : ''}`}>
                <label>Telefone de contato <span className="obrigatorio">*</span></label>
                <input type="text" placeholder="(XX) XXXXX-XXXX"
                  value={form.telefone} onChange={e => atualizarTelefone(e.target.value)} />
                {erros.telefone && <span className="mensagem-erro">{erros.telefone}</span>}
              </div>
            </div>
          </div>

          <div className="cadastro-secao">
            <h2>Dados da Internação</h2>
            <div className="cadastro-grade">
              <div className={`campo ${erros.baia ? 'campo--erro' : ''}`}>
                <label>Baia <span className="obrigatorio">*</span></label>
                {baiasVazias.length > 0 ? (
                  <select value={form.baia} onChange={e => atualizar('baia', e.target.value)}>
                    {baiasVazias.map(b => (
                      <option key={b.id_baia} value={b.id_baia}>
                        Baia {b.numero}
                      </option>
                    ))}
                  </select>
                ) : (
                  <p className="campo-aviso">Nenhuma baia disponível.</p>
                )}
                {erros.baia && <span className="mensagem-erro">{erros.baia}</span>}
              </div>
              <div className="campo">
                <label>Data de entrada</label>
                <input type="date" value={form.dataEntrada}
                  onChange={e => atualizar('dataEntrada', e.target.value)} />
              </div>
              <div className={`campo ${erros.veterinario ? 'campo--erro' : ''}`}>
                <label>Veterinário responsável <span className="obrigatorio">*</span></label>
                <input type="text" placeholder="Ex: Dra. Ana"
                  value={form.veterinario} onChange={e => atualizar('veterinario', e.target.value)} />
                {erros.veterinario && <span className="mensagem-erro">{erros.veterinario}</span>}
              </div>
              <div className="campo">
                <label>Alergias conhecidas</label>
                <input type="text" placeholder="Ex: Nenhuma"
                  value={form.alergias} onChange={e => atualizar('alergias', e.target.value)} />
              </div>
              <div className={`campo campo--largo ${erros.motivo ? 'campo--erro' : ''}`}>
                <label>Motivo da internação <span className="obrigatorio">*</span></label>
                <input type="text" placeholder="Ex: Cirurgia de castração"
                  value={form.motivo} onChange={e => atualizar('motivo', e.target.value)} />
                {erros.motivo && <span className="mensagem-erro">{erros.motivo}</span>}
              </div>
              <div className="campo campo--cheio">
                <label>Diagnóstico inicial</label>
                <textarea placeholder="Descreva o diagnóstico inicial..."
                  value={form.diagnostico} onChange={e => atualizar('diagnostico', e.target.value)} />
              </div>
              <div className="campo campo--cheio">
                <label>Medicamentos em uso</label>
                <textarea placeholder="Liste os medicamentos e doses..."
                  value={form.medicamentos} onChange={e => atualizar('medicamentos', e.target.value)} />
              </div>
            </div>
          </div>

          <div className="cadastro-rodape-info">
            <span className="obrigatorio">*</span> Campos obrigatórios
          </div>

          {erroCadastro && <p className="mensagem-erro">{erroCadastro}</p>}

          <div className="cadastro-acoes">
            <button type="button" className="botao-cancelar" onClick={() => navegar('/painel')}>
              Cancelar
            </button>
            <button type="submit" className="botao-cadastrar" disabled={salvando}>
              {salvando ? 'Salvando...' : 'Cadastrar Animal'}
            </button>
          </div>

        </form>
      </main>
    </div>
  )
}
