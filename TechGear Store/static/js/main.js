document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach((alert) => {
    window.setTimeout(() => { if (window.bootstrap) bootstrap.Alert.getOrCreateInstance(alert).close(); }, 5000);
  });
  document.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener('change', () => {
      const min = Number(input.min || 0), max = Number(input.max || 99999);
      input.value = Math.max(min, Math.min(max, Number(input.value || min)));
    });
  });
});
