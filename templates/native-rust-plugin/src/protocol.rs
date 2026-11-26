use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::io::{self, Write};
use std::sync::{Arc, Mutex};

fn default_true() -> bool {
    true
}

/// Declarative configuration row rendered natively in Ballista's Property Inspector
/// and Plugin Settings dialog.
#[derive(Debug, Deserialize, Serialize, Clone, PartialEq)]
pub struct BridgeConfigRow {
    pub index: usize,
    #[serde(rename = "type")]
    pub row_type: String, // EntryRow, PasswordRow, SwitchRow, ComboRow, SpinRow, ScaleRow, ColorRow, ButtonRow, ActionRow
    pub title: String,
    #[serde(default)]
    pub subtitle: String,
    #[serde(default = "default_true")]
    pub visible: bool,
    #[serde(default = "default_true")]
    pub sensitive: bool,
    #[serde(default = "default_true")]
    pub editable: bool,
    #[serde(default)]
    pub options: Vec<String>,
    #[serde(default)]
    pub selected: usize,
    #[serde(default)]
    pub active: bool,
    #[serde(default)]
    pub text: String,
    #[serde(default)]
    pub value: f64,
    #[serde(default)]
    pub min: f64,
    #[serde(default)]
    pub max: f64,
    #[serde(default)]
    pub step: f64,
    #[serde(default)]
    pub digits: u32,
    #[serde(default)]
    pub color: String,
    #[serde(default)]
    pub button_icon: String,
    #[serde(default)]
    pub button_label: String,
    #[serde(default)]
    pub suggested: bool,
}

impl BridgeConfigRow {
    pub fn new(index: usize, row_type: &str, title: &str) -> Self {
        Self {
            index,
            row_type: row_type.to_string(),
            title: title.to_string(),
            subtitle: String::new(),
            visible: true,
            sensitive: true,
            editable: true,
            options: Vec::new(),
            selected: 0,
            active: false,
            text: String::new(),
            value: 0.0,
            min: 0.0,
            max: 100.0,
            step: 1.0,
            digits: 0,
            color: "#9146ff".to_string(),
            button_icon: String::new(),
            button_label: String::new(),
            suggested: false,
        }
    }
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct BridgeActionMeta {
    pub action_id: String,
    pub action_name: String,
    #[serde(default)]
    pub icon_path: String,
    #[serde(default)]
    pub icon_name: String,
    #[serde(default = "default_true")]
    pub supports_key: bool,
    #[serde(default = "default_true")]
    pub supports_dial: bool,
    #[serde(default = "default_true")]
    pub supports_touchscreen: bool,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize, Default)]
pub struct BridgeCommand {
    pub cmd: String,
    #[serde(default)]
    pub plugin_id: Option<String>,
    #[serde(default)]
    pub plugin_path: Option<String>,
    #[serde(default)]
    pub slot: Option<String>,
    #[serde(default)]
    pub action_id: Option<String>,
    #[serde(default)]
    pub settings: Option<HashMap<String, Value>>,
    #[serde(default)]
    pub event: Option<String>,
    #[serde(default)]
    pub delta: Option<i32>,
    #[serde(default)]
    pub index: Option<usize>,
    #[serde(default)]
    pub selected: Option<usize>,
    #[serde(default)]
    pub active: Option<bool>,
    #[serde(default)]
    pub text: Option<String>,
    #[serde(default)]
    pub color: Option<String>,
    #[serde(default)]
    pub value: Option<f64>,
    #[serde(default)]
    pub trigger_button: Option<bool>,
    #[serde(default)]
    pub norm_x: Option<f64>,
    #[serde(default)]
    pub norm_y: Option<f64>,
}

#[allow(dead_code)]
#[derive(Debug, Serialize, Clone)]
#[serde(tag = "event")]
pub enum BridgeEvent {
    #[serde(rename = "plugin_initialized")]
    PluginInitialized {
        plugin_id: String,
        plugin_name: String,
        has_settings: bool,
        selector_icon_path: String,
        selector_icon_name: String,
        actions: Vec<BridgeActionMeta>,
    },
    #[serde(rename = "set_media")]
    SetMedia {
        slot: String,
        media_path: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        size: Option<f64>,
    },
    #[serde(rename = "set_label")]
    SetLabel {
        slot: String,
        text: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        position: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        color: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        font_size: Option<u32>,
    },
    #[serde(rename = "set_settings")]
    SetSettings {
        slot: String,
        settings: HashMap<String, Value>,
    },
    #[serde(rename = "action_config_rows")]
    ActionConfigRows {
        slot: String,
        rows: Vec<BridgeConfigRow>,
    },
    #[serde(rename = "plugin_settings_rows")]
    PluginSettingsRows {
        plugin_id: String,
        rows: Vec<BridgeConfigRow>,
    },
    #[serde(rename = "show_error")]
    ShowError { slot: String, duration: i32 },
}

#[derive(Clone)]
pub struct HostEmitter {
    lock: Arc<Mutex<()>>,
}

impl HostEmitter {
    pub fn new() -> Self {
        Self {
            lock: Arc::new(Mutex::new(())),
        }
    }

    pub fn emit(&self, ev: &BridgeEvent) {
        if let Ok(line) = serde_json::to_string(ev) {
            let _guard = self.lock.lock().unwrap();
            let mut out = io::stdout().lock();
            let _ = out.write_all(line.as_bytes());
            let _ = out.write_all(b"\n");
            let _ = out.flush();
        }
    }

    #[allow(dead_code)]
    pub fn set_media(&self, slot: &str, media_path: &str, size: Option<f64>) {
        self.emit(&BridgeEvent::SetMedia {
            slot: slot.to_string(),
            media_path: media_path.to_string(),
            size,
        });
    }

    pub fn set_label(&self, slot: &str, position: &str, text: &str, font_size: Option<u32>) {
        self.emit(&BridgeEvent::SetLabel {
            slot: slot.to_string(),
            text: text.to_string(),
            position: Some(position.to_string()),
            color: None,
            font_size,
        });
    }

    pub fn set_settings(&self, slot: &str, settings: HashMap<String, Value>) {
        self.emit(&BridgeEvent::SetSettings {
            slot: slot.to_string(),
            settings,
        });
    }
}
