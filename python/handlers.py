# Probe Basic (QtPyVCP) notifier for safety interlocks.
from qtpyvcp import hal
try:
    from qtpyvcp.utilities.notifications import notify  # newer QtPyVCP
except Exception:
    from qtpyvcp.utilities import notify                # fallback

NICE = {
    'air-fault':      'Air pressure low',
    'temp-fault':     'Spindle temperature fault',
    'toollock-fault': 'Tool not clamped',
}

class SafetyNotifier(object):
    def __init__(self, vcp=None):
        # Track current active list to avoid spamming
        self._last_active = None
        # Subscribe to HAL **signals**
        self.sigs = {}
        for name in NICE:
            sig = hal.getSignal(name)
            if sig is None:
                print(f"[SafetyNotifier] WARNING: HAL signal '{name}' not found.")
                continue
            self.sigs[name] = sig
            sig.valueChanged.connect(self._on_change)

        print("[SafetyNotifier] Loaded. Watching:", ", ".join(self.sigs.keys()))
        self._on_change()  # fire once

    def _on_change(self, *_, **__):
        active = tuple(sorted(k for k, s in self.sigs.items() if getattr(s, "value", False)))
        if active == self._last_active:
            return  # no change

        self._last_active = active
        if active:
            # Sticky ERROR until fixed; also appears in STATUS tab
            lines = "\n• ".join(NICE[k] for k in active)
            notify.error("Start inhibited:\n• " + lines, timeout=0)
        else:
            notify.info("All safety interlocks OK", timeout=2000)

def init_safety_notifier(vcp=None):
    print("[SafetyNotifier] init called")
    SafetyNotifier(vcp)
