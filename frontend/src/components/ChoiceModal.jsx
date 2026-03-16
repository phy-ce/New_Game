import '../styles/ChoiceModal.css';

export default function ChoiceModal({ pendingChoice, onResolve }) {
  if (!pendingChoice) return null;

  return (
    <div className="choice-overlay">
      <div className="choice-modal">
        <div className="cm-prompt">{pendingChoice.prompt}</div>
        <div className="cm-options">
          {pendingChoice.options.map((option, i) => (
            <button
              key={i}
              className="cm-option"
              onClick={() => onResolve(option)}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
