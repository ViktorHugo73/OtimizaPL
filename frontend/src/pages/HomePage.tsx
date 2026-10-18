import { Link } from 'react-router-dom';
import './home.css';

const instructions = [
  'Crie um problema e informe um nome para identificá-lo.',
  'Cadastre as decisões, definindo as variáveis que representam o que deve ser calculado.',
  'Defina o objetivo, escolhendo entre minimizar ou maximizar e informando os coeficientes de cada variável.',
  'Adicione as restrições, informando os limites de recursos, demanda, capacidade ou outras condições do problema.',
  'Revise os dados cadastrados antes de executar.',
  'Execute a otimização para obter a melhor solução encontrada pelo sistema.',
  'Analise o resultado, verificando o valor ótimo, as decisões calculadas e a utilização dos recursos.',
  'Crie cenários para modificar parâmetros e comparar diferentes alternativas.',
];
const features = [
  'Cadastro de problemas de Programação Linear',
  'Minimização e maximização da função objetivo',
  'Resolução pelo Método Simplex',
  'Visualização da solução ótima e dos valores das variáveis',
  'Análise de folgas, excessos e utilização dos recursos',
  'Identificação de restrições ativas',
  'Criação e comparação de cenários',
  'Consulta ao histórico de execuções',
  'Registro dos resultados para análise posterior',
];

export default function HomePage() {
  return <main className="how-to-page">
    <h1>Como usar?</h1>
    <section className="how-to-intro" aria-labelledby="simplex-title">
      <h2 id="simplex-title">O que é o Método Simplex?</h2>
      <p>O Método Simplex é um algoritmo utilizado para resolver problemas de Programação Linear. Ele busca encontrar a melhor solução possível para um objetivo, como minimizar custos ou maximizar resultados, respeitando os limites e recursos disponíveis.</p>
    </section>
    <section aria-labelledby="instructions-title">
      <h2 id="instructions-title">Como usar</h2>
      <ol>{instructions.map(item => <li key={item}>{item}</li>)}</ol>
    </section>
    <section aria-labelledby="features-title">
      <h2 id="features-title">Recursos</h2>
      <ul>{features.map(item => <li key={item}>{item}</li>)}</ul>
    </section>
    <nav className="how-to-actions" aria-label="Começar a usar"><Link to="/problems/new">Criar um problema</Link><Link to="/problems">Ver problemas cadastrados</Link></nav>
  </main>;
}
