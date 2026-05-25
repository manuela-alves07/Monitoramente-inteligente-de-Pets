import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PaginaLogin from './paginas/PaginaLogin'
import PaginaPainel from './paginas/PaginaPainel'
import PaginaDetalhesPet from './paginas/PaginaDetalhesPet'
import PaginaCadastroPet from './paginas/PaginaCadastroPet'
import PaginaConfiguracoes from './paginas/PaginaConfiguracoes'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"                element={<PaginaLogin />} />
        <Route path="/painel"          element={<PaginaPainel />} />
        <Route path="/baia/:numero"    element={<PaginaDetalhesPet />} />
        <Route path="/cadastro"        element={<PaginaCadastroPet />} />
        <Route path="/configuracoes"   element={<PaginaConfiguracoes />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
