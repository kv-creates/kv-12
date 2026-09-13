
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, os
out='assets'
os.makedirs(out, exist_ok=True)
os.makedirs('docs/images', exist_ok=True)
# metrics
fig,ax=plt.subplots(figsize=(10,4), facecolor='#0A0E1A')
ax.set_facecolor('#0A0E1A')
tasks=['HumanEvalFix','Defects4J','CVEFixes','CodeReview']
kv12=[82,94,90,79]
gpt=[78,88,86,72]
x=np.arange(len(tasks)); w=0.35
ax.bar(x-w/2,kv12,w,color='#00D9FF',label='KV-12',edgecolor='#00D9FF')
ax.bar(x+w/2,gpt,w,color='#7C3AED',label='GPT-4',edgecolor='#7C3AED')
ax.set_xticks(x); ax.set_xticklabels(tasks,color='white')
ax.set_ylabel('Score',color='white'); ax.tick_params(colors='white')
ax.set_title('KV-12 vs GPT-4 — Benchmarks',color='white')
ax.legend(facecolor='#0F1420',labelcolor='white',edgecolor='rgba(255,255,255,.1)')
for spine in ax.spines.values(): spine.set_color('rgba(255,255,255,.1)')
fig.tight_layout(); fig.savefig('assets/metrics.svg'); fig.savefig('docs/images/metrics.png', dpi=150, facecolor=fig.get_facecolor()); plt.close(fig)
# architecture minimal
fig,ax=plt.subplots(figsize=(10,2.5),facecolor='#0A0E1A')
ax.set_facecolor('#0A0E1A'); ax.axis('off')
labels=['Code+AST','Tokenizer','12B Backbone','Repo-Graph','Heads']
for i,lab in enumerate(labels):
    ax.add_patch(plt.Rectangle((i*2+0.2,0.4),1.6,0.6,facecolor='#0F1420',edgecolor='#00D9FF',lw=1.2))
    ax.text(i*2+1.0,0.7,lab,ha='center',va='center',color='white',fontsize=9, family='monospace')
    if i<4: ax.arrow(i*2+1.8,0.7,0.4,0,head_width=0.08,head_length=0.1,color='#7C3AED',length_includes_head=True)
ax.set_xlim(0,10); ax.set_ylim(0,1.2); ax.set_title('KV-12 Architecture — Minimalist',color='white',fontsize=11)
fig.tight_layout(); fig.savefig('assets/architecture-minimal.svg'); fig.savefig('docs/images/architecture.png', dpi=150, facecolor=fig.get_facecolor()); plt.close(fig)
# banner
fig,ax=plt.subplots(figsize=(12,3.2),facecolor='#0A0E1A')
ax.set_facecolor('#0A0E1A'); ax.axis('off')
ax.text(0.5,0.65,'KV-12',ha='center',va='center',color='white',fontsize=48,weight='900',family='monospace')
ax.text(0.5,0.35,'The Precise Code Intelligence Engine — 12B Minimalist',ha='center',va='center',color='#9AA3B2',fontsize=12)
# accent line
ax.plot([0.2,0.8],[0.15,0.15],color='#00D9FF',lw=2,transform=ax.transAxes)
fig.tight_layout(); fig.savefig('assets/banner-minimal.svg'); fig.savefig('docs/images/banner.png', dpi=150, facecolor=fig.get_facecolor()); plt.close(fig)
# latency
fig,ax=plt.subplots(figsize=(6,3),facecolor='white')
xs=[100,500,1000,2000,4000]
kv=[0.2,0.4,0.8,1.4,2.6]
gpt=[0.6,1.2,2.4,4.2,8.0]
ax.plot(xs,kv,color='#00D9FF',marker='o',label='KV-12')
ax.plot(xs,gpt,color='#7C3AED',marker='s',label='GPT-4')
ax.set_xlabel('Tokens'); ax.set_ylabel('Latency s'); ax.set_title('Latency vs Tokens')
ax.legend(); fig.tight_layout(); fig.savefig('docs/images/latency.png', dpi=150); plt.close(fig)
print('graphics done')
