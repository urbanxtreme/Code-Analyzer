import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer" id="main-footer">
      <div className="container footer-inner">
        <div className="footer-left">
          <span>Built with 🧠 by</span>
          <span className="gradient-text">RepoIntel</span>
        </div>
        <div className="footer-right">
          <div className="footer-tech">
            <span>React</span>
            <span className="footer-dot"></span>
            <span>FastAPI</span>
            <span className="footer-dot"></span>
            <span>Ollama</span>
          </div>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
          >
            Open Source
          </a>
        </div>
      </div>
    </footer>
  );
}
