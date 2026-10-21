"""Check a constructed state, not empirical model behavior or study results."""
from morph_fl.domain import FaultHypothesis, Prediction, SourceLocation
from morph_fl.search.policies import PlateauMonitor, SearchSample, distance, select_portfolio

def hypothesis(label, path, mechanism, score):
    return FaultHypothesis(label, [SourceLocation(path, 2, 2, 'illustration', 'illustration')], mechanism, [Prediction(label+'p', 'illustrative source predicate')], score=score)
a = hypothesis('hA', 'handler.py', 'handler bypasses normalization', -1)
b = hypothesis('hB', 'config.py', 'default overrides false', 1)
assert abs(distance(a,b)-1) < 1e-12
assert [h.id for h in select_portfolio([a,b],3)] == ['hB','hA']
monitor=PlateauMonitor(total_budget=16000)
for gain,repetition in [(2,0),(0,1),(0,1),(0,1)]:
    monitor.update(SearchSample(gain,repetition,distance(a,b),512))
remaining=16000-4*512
decision=monitor.evaluate(remaining,256)
assert abs(decision['consumed_fraction']-.128)<1e-12
assert decision['should_reset'] is True
assert decision['window']==3 and decision['evidence_gain']==0
assert decision['window_tokens']==1536 and remaining==13952
print('Synthetic trace checked: portfolio hB,hA; reset true; no empirical claims.')
