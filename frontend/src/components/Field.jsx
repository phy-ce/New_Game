import { useState, useRef, useEffect } from 'react';
import UnitCard from './UnitCard';
import '../styles/Field.css';


const SLOT_LIMIT = 7;

export default function Field({ units, isMe, onTargetUnit }) {
  const [expandedStack, setExpandedStack] = useState(null);
  const prevIdsRef = useRef(new Set());
  const [newIds, setNewIds] = useState(new Set());

  useEffect(() => {
    const currentIds = new Set(units.map(u => u.id));
    const added = new Set([...currentIds].filter(id => !prevIdsRef.current.has(id)));
    if (added.size > 0) {
      setNewIds(added);
      const timer = setTimeout(() => setNewIds(new Set()), 400);
      prevIdsRef.current = currentIds;
      return () => clearTimeout(timer);
    }
    prevIdsRef.current = currentIds;
  }, [units]);

  // Close popup when targeting mode ends
  useEffect(() => {
    if (!onTargetUnit) setExpandedStack(null);
  }, [onTargetUnit]);

  // Close popup on click outside
  useEffect(() => {
    if (!expandedStack) return;
    const handler = () => setExpandedStack(null);
    document.addEventListener('click', handler);
    return () => document.removeEventListener('click', handler);
  }, [expandedStack]);

  const handleStackClick = (name) => {
    setExpandedStack(expandedStack === name ? null : name);
  };

  const handleTargetFromPopup = (unitId, stackName) => {
    setExpandedStack(null);
    onTargetUnit(unitId);
  };

  const shouldStack = units.length > SLOT_LIMIT;

  if (!shouldStack) {
    return (
      <div className={`field ${isMe ? 'field-me' : 'field-opponent'}`}>
        {units.map(unit => (
          <UnitCard
            key={unit.id}
            unit={unit}
            isNew={newIds.has(unit.id)}
            onTarget={onTargetUnit ? () => onTargetUnit(unit.id) : undefined}
          />
        ))}
      </div>
    );
  }

  const stacks = {};
  for (const unit of units) {
    if (!stacks[unit.name]) stacks[unit.name] = [];
    stacks[unit.name].push(unit);
  }
  const stackEntries = Object.entries(stacks);
  const visible = stackEntries.slice(0, SLOT_LIMIT);
  const overflow = stackEntries.length - SLOT_LIMIT;

  return (
    <div className={`field ${isMe ? 'field-me' : 'field-opponent'}`}>
      {visible.map(([name, unitList]) => (
        <div
          key={name}
          className={`unit-stack-slot ${onTargetUnit ? 'targetable' : ''}`}
          onClick={(e) => { e.stopPropagation(); handleStackClick(name); }}
        >
          <UnitCard unit={unitList[0]} stackCount={unitList.length} isNew={newIds.has(unitList[0].id)} />
          {expandedStack === name && (
            <div className="stack-popup" onClick={e => e.stopPropagation()}>
              {unitList.map(u => (
                <UnitCard
                  key={u.id}
                  unit={u}
                  onTarget={onTargetUnit ? () => handleTargetFromPopup(u.id, name) : undefined}
                />
              ))}
            </div>
          )}
        </div>
      ))}
      {overflow > 0 && (
        <div className="stack-overflow">+{overflow} more</div>
      )}
    </div>
  );
}
