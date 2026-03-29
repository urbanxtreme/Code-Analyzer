import { BrowserRouter as Router } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import LoadingState from './components/LoadingState';
import ErrorDisplay from './components/ErrorDisplay';
import HomePage from './pages/HomePage';
import ReportPage from './pages/ReportPage';
import { useAnalyze } from './hooks/useAnalyze';

export default function App() {
  const { report, loading, error, currentStep, analyze, reset } = useAnalyze(false);

  const handleAnalyze = (repoUrl) => {
    analyze(repoUrl);
  };

  const handleReset = () => {
    reset();
  };

  return (
    <Router>
      <Header />

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Error State */}
        {error && !loading && (
          <ErrorDisplay
            message={error}
            onRetry={() => handleAnalyze('')}
            onBack={handleReset}
          />
        )}

        {/* Loading State */}
        {loading && <LoadingState currentStep={currentStep} />}

        {/* Report View */}
        {report && !loading && !error && (
          <ReportPage report={report} onReset={handleReset} />
        )}

        {/* Home View */}
        {!report && !loading && !error && (
          <HomePage onAnalyze={handleAnalyze} loading={loading} />
        )}
      </main>

      <Footer />
    </Router>
  );
}
