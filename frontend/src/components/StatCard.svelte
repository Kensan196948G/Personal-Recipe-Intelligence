<script>
  export let icon = '';
  export let title = '';
  export let value = 0;
  export let subtitle = '';
  export let color = 'blue';
</script>

<div class="stat-card stat-card--{color}">
  <div class="stat-icon">{icon}</div>
  <div class="stat-content">
    <div class="stat-value">{value}</div>
    <div class="stat-title">{title}</div>
    {#if subtitle}
      <div class="stat-subtitle">{subtitle}</div>
    {/if}
  </div>
</div>

<style>
  .stat-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  }

  .stat-icon {
    font-size: 2rem;
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: #f0f7ff;
  }

  .stat-card--blue .stat-icon { background: #e3f2fd; }
  .stat-card--green .stat-icon { background: #e8f5e9; }
  .stat-card--orange .stat-icon { background: #fff3e0; }
  .stat-card--purple .stat-icon { background: #f3e5f5; }
  .stat-card--red .stat-icon { background: #ffebee; }

  .stat-content {
    flex: 1;
  }

  .stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.2;
  }

  .stat-title {
    font-size: 0.875rem;
    color: #666;
    margin-top: 0.25rem;
  }

  .stat-subtitle {
    font-size: 0.75rem;
    color: #999;
    margin-top: 0.25rem;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .stat-card {
      flex-direction: column;
      text-align: center;
      padding: 1rem;
      gap: 0.5rem;
    }

    .stat-icon {
      width: 48px;
      height: 48px;
      font-size: 1.5rem;
    }

    .stat-value {
      font-size: 1.5rem;
    }

    .stat-title {
      font-size: 0.75rem;
    }
  }
</style>
