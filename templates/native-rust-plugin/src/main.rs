mod protocol;

use protocol::{BridgeActionMeta, BridgeCommand, BridgeConfigRow, BridgeEvent, HostEmitter};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};

// Update these constants to match your manifest.json!
const PLUGIN_ID: &str = "com_yourhandle_MyPlugin";
const PLUGIN_NAME: &str = "My Plugin";

#[derive(Debug, Clone, Serialize, Deserialize)]
struct PluginSettings {
    greeting: String,
    verbose: bool,
}

impl Default for PluginSettings {
    fn default() -> Self {
        Self {
            greeting: "Hello Ballista!".into(),
            verbose: false,
        }
    }
}

struct SlotState {
    action_id: String,
    settings: HashMap<String, Value>,
    count: i64,
}

fn load_settings(data_dir: &Path) -> PluginSettings {
    let p = data_dir.join("settings.json");
    std::fs::read_to_string(&p)
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

fn save_settings(data_dir: &Path, cfg: &PluginSettings) {
    let _ = std::fs::create_dir_all(data_dir);
    if let Ok(raw) = serde_json::to_string_pretty(cfg) {
        let _ = std::fs::write(data_dir.join("settings.json"), raw);
    }
}

fn resolve_asset(plugin_dir: &Path, filename: &str) -> Option<String> {
    let p = plugin_dir.join("assets").join(filename);
    p.is_file().then(|| p.to_string_lossy().to_string())
}

fn action_stem(action_id: &str) -> &str {
    action_id.rsplit("::").next().unwrap_or(action_id)
}

fn build_plugin_settings_rows(cfg: &PluginSettings, status: &str) -> Vec<BridgeConfigRow> {
    let mut r0 = BridgeConfigRow::new(0, "EntryRow", "Default Greeting");
    r0.text = cfg.greeting.clone();

    let mut r1 = BridgeConfigRow::new(1, "SwitchRow", "Verbose Logging");
    r1.subtitle = "Log extra diagnostics to stderr".into();
    r1.active = cfg.verbose;

    let mut r2 = BridgeConfigRow::new(2, "ButtonRow", "Plugin Status");
    r2.subtitle = status.to_string();
    r2.button_label = "Ping".into();
    r2.suggested = true;

    vec![r0, r1, r2]
}

fn build_action_config_rows(inst: &SlotState) -> Vec<BridgeConfigRow> {
    match action_stem(&inst.action_id) {
        "CounterAction" => {
            let step = inst
                .settings
                .get("step")
                .and_then(|v| v.as_f64())
                .unwrap_or(1.0);
            let mut r0 = BridgeConfigRow::new(0, "SpinRow", "Step Size");
            r0.subtitle = "Amount added per key press or dial tick".into();
            r0.min = 1.0;
            r0.max = 25.0;
            r0.step = 1.0;
            r0.value = step;

            let mut r1 = BridgeConfigRow::new(1, "ButtonRow", "Counter Value");
            r1.subtitle = format!("Current count: {}", inst.count);
            r1.button_label = "Reset".into();

            vec![r0, r1]
        }
        _ => {
            let label = inst
                .settings
                .get("label")
                .and_then(|v| v.as_str())
                .unwrap_or("Trigger");
            let mut r0 = BridgeConfigRow::new(0, "EntryRow", "Key Label");
            r0.text = label.to_string();
            vec![r0]
        }
    }
}

fn render_slot(plugin_dir: &Path, emitter: &HostEmitter, slot: &str, inst: &SlotState) {
    match action_stem(&inst.action_id) {
        "CounterAction" => {
            if let Some(ic) = resolve_asset(plugin_dir, "counter.png") {
                emitter.set_media(slot, &ic, Some(1.0));
            }
            emitter.set_label(slot, "center", &inst.count.to_string(), Some(20));
        }
        _ => {
            if let Some(ic) = resolve_asset(plugin_dir, "quick_action.png") {
                emitter.set_media(slot, &ic, Some(1.0));
            }
            let lbl = inst
                .settings
                .get("label")
                .and_then(|v| v.as_str())
                .unwrap_or("Trigger");
            emitter.set_label(slot, "bottom", lbl, Some(12));
        }
    }
}

fn main() {
    let plugin_dir = std::env::var("BALLISTA_PLUGIN_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|_| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")));
    let data_dir = std::env::var("BALLISTA_DATA_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|_| plugin_dir.join(".data"));

    let mut cfg = load_settings(&data_dir);
    let mut status = "Ready".to_string();
    let mut slots: HashMap<String, SlotState> = HashMap::new();
    let emitter = HostEmitter::new();

    let stdin = io::stdin();
    for line in stdin.lock().lines().map_while(Result::ok) {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        let Ok(cmd) = serde_json::from_str::<BridgeCommand>(trimmed) else {
            continue;
        };

        match cmd.cmd.as_str() {
            "init_plugin" => {
                let icon_or = |file: &str, sym: &str| {
                    if let Some(p) = resolve_asset(&plugin_dir, file) {
                        (p, String::new())
                    } else {
                        (String::new(), sym.to_string())
                    }
                };
                let (c_path, c_sym) = icon_or("counter.png", "list-add-symbolic");
                let (q_path, q_sym) = icon_or("quick_action.png", "system-run-symbolic");

                emitter.emit(&BridgeEvent::PluginInitialized {
                    plugin_id: PLUGIN_ID.to_string(),
                    plugin_name: PLUGIN_NAME.to_string(),
                    has_settings: true,
                    selector_icon_path: resolve_asset(&plugin_dir, "icon.png").unwrap_or_default(),
                    selector_icon_name: "application-x-executable-symbolic".to_string(),
                    actions: vec![
                        BridgeActionMeta {
                            action_id: format!("{PLUGIN_ID}::CounterAction"),
                            action_name: "Counter".into(),
                            icon_path: c_path,
                            icon_name: c_sym,
                            supports_key: true,
                            supports_dial: true,
                            supports_touchscreen: true,
                        },
                        BridgeActionMeta {
                            action_id: format!("{PLUGIN_ID}::QuickAction"),
                            action_name: "Quick Action".into(),
                            icon_path: q_path,
                            icon_name: q_sym,
                            supports_key: true,
                            supports_dial: false,
                            supports_touchscreen: false,
                        },
                    ],
                });
            }
            "create_action" => {
                if let (Some(slot), Some(action_id)) = (cmd.slot, cmd.action_id) {
                    let settings = cmd.settings.unwrap_or_default();
                    let count = settings.get("count").and_then(|v| v.as_i64()).unwrap_or(0);
                    let inst = SlotState {
                        action_id,
                        settings,
                        count,
                    };
                    let rows = build_action_config_rows(&inst);
                    render_slot(&plugin_dir, &emitter, &slot, &inst);
                    emitter.emit(&BridgeEvent::ActionConfigRows {
                        slot: slot.clone(),
                        rows,
                    });
                    slots.insert(slot, inst);
                }
            }
            "destroy_action" => {
                if let Some(slot) = cmd.slot {
                    slots.remove(&slot);
                }
            }
            "clear_all_actions" => slots.clear(),
            "clear_device_actions" => {
                if let Some(dev_key) = cmd.slot {
                    let prefix = format!("{dev_key}::");
                    slots.retain(|s, _| !s.starts_with(&prefix));
                }
            }
            "get_plugin_settings_rows" => {
                emitter.emit(&BridgeEvent::PluginSettingsRows {
                    plugin_id: PLUGIN_ID.to_string(),
                    rows: build_plugin_settings_rows(&cfg, &status),
                });
            }
            "set_plugin_settings_row" => {
                match cmd.index.unwrap_or(usize::MAX) {
                    0 => {
                        if let Some(t) = cmd.text {
                            cfg.greeting = t;
                        }
                    }
                    1 => {
                        if let Some(a) = cmd.active {
                            cfg.verbose = a;
                        }
                    }
                    _ => {}
                }
                save_settings(&data_dir, &cfg);
            }
            "trigger_plugin_settings_button" => {
                if cmd.index == Some(2) {
                    status = format!("OK — {}", cfg.greeting);
                    emitter.emit(&BridgeEvent::PluginSettingsRows {
                        plugin_id: PLUGIN_ID.to_string(),
                        rows: build_plugin_settings_rows(&cfg, &status),
                    });
                }
            }
            "get_action_config_rows" => {
                if let Some(slot) = cmd.slot {
                    if let Some(inst) = slots.get(&slot) {
                        emitter.emit(&BridgeEvent::ActionConfigRows {
                            slot,
                            rows: build_action_config_rows(inst),
                        });
                    }
                }
            }
            "set_action_config_row" => {
                if let Some(slot) = cmd.slot {
                    if let Some(inst) = slots.get_mut(&slot) {
                        match action_stem(&inst.action_id) {
                            "CounterAction" if cmd.index == Some(0) => {
                                if let Some(val) = cmd.value {
                                    inst.settings.insert("step".into(), json!(val.clamp(1.0, 25.0)));
                                }
                            }
                            "QuickAction" if cmd.index == Some(0) => {
                                if let Some(txt) = cmd.text {
                                    inst.settings.insert("label".into(), json!(txt));
                                }
                            }
                            _ => {}
                        }
                        emitter.set_settings(&slot, inst.settings.clone());
                        render_slot(&plugin_dir, &emitter, &slot, inst);
                    }
                }
            }
            "trigger_action_config_button" => {
                if let Some(slot) = cmd.slot {
                    if let Some(inst) = slots.get_mut(&slot) {
                        if action_stem(&inst.action_id) == "CounterAction" && cmd.index == Some(1) {
                            inst.count = 0;
                            inst.settings.insert("count".into(), json!(0));
                            emitter.set_settings(&slot, inst.settings.clone());
                            render_slot(&plugin_dir, &emitter, &slot, inst);
                            emitter.emit(&BridgeEvent::ActionConfigRows {
                                slot,
                                rows: build_action_config_rows(inst),
                            });
                        }
                    }
                }
            }
            "key_event" => {
                if cmd.event.as_deref() == Some("down") {
                    if let Some(slot) = cmd.slot {
                        if let Some(inst) = slots.get_mut(&slot) {
                            if action_stem(&inst.action_id) == "CounterAction" {
                                let step = inst.settings.get("step").and_then(|v| v.as_f64()).unwrap_or(1.0) as i64;
                                inst.count += step;
                                inst.settings.insert("count".into(), json!(inst.count));
                                emitter.set_settings(&slot, inst.settings.clone());
                                render_slot(&plugin_dir, &emitter, &slot, inst);
                                emitter.emit(&BridgeEvent::ActionConfigRows {
                                    slot,
                                    rows: build_action_config_rows(inst),
                                });
                            }
                        }
                    }
                }
            }
            "dial_event" => {
                if let Some(slot) = cmd.slot {
                    if let Some(inst) = slots.get_mut(&slot) {
                        if action_stem(&inst.action_id) == "CounterAction" {
                            let step = inst.settings.get("step").and_then(|v| v.as_f64()).unwrap_or(1.0) as i64;
                            match cmd.event.as_deref().unwrap_or("") {
                                "turn" => inst.count += (cmd.delta.unwrap_or(0) as i64) * step,
                                "press" => inst.count += step,
                                "tap" => inst.count = 0, // Tap touchscreen to reset
                                _ => {}
                            }
                            inst.settings.insert("count".into(), json!(inst.count));
                            emitter.set_settings(&slot, inst.settings.clone());
                            render_slot(&plugin_dir, &emitter, &slot, inst);
                            emitter.emit(&BridgeEvent::ActionConfigRows {
                                slot,
                                rows: build_action_config_rows(inst),
                            });
                        }
                    }
                }
            }
            "shutdown" => break,
            _ => {}
        }
    }
}
