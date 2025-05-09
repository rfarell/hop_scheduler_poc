import json, pandas as pd, matplotlib.pyplot as plt, os, sys
data=[]
with open('results/run.jsonl') as f:
    for ln in f:
        data.append(json.loads(ln))
df=pd.DataFrame(data)
plt.plot(df['frame'], df['pdr'])
plt.xlabel('Frame'); plt.ylabel('Packet‑delivery ratio')
plt.title('PDR vs Time')
plt.savefig('results/pdr.png', dpi=300)
print('Saved results/pdr.png')
df[['pdr','latency']].rolling(50).mean().to_csv('results/rolling.csv', index=False)
