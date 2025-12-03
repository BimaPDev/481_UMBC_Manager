import { useState, useEffect } from "react";
import type { Settings } from "../types";

const API_URL = "http://localhost:8000";

export default function SettingsPage() {
    const [settings, setSettings] = useState<Settings | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

    useEffect(() => {
        fetch(`${API_URL}/settings`)
            .then((res) => res.json())
            .then((data) => {
                setSettings(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Failed to load settings:", err);
                setMessage({ text: "Failed to load settings", type: "error" });
                setLoading(false);
            });
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!settings) return;
        setSettings({ ...settings, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!settings) return;

        setSaving(true);
        setMessage(null);

        fetch(`${API_URL}/settings`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(settings),
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to save");
                return res.json();
            })
            .then(() => {
                setMessage({ text: "Settings saved successfully!", type: "success" });
            })
            .catch((err) => {
                console.error("Failed to save settings:", err);
                setMessage({ text: "Failed to save settings", type: "error" });
            })
            .finally(() => {
                setSaving(false);
            });
    };

    if (loading) return <div className="p-8 text-center">Loading settings...</div>;
    if (!settings) return <div className="p-8 text-center text-red-500">Error loading settings.</div>;

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md mt-10">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Application Settings</h2>

            {message && (
                <div className={`p-4 mb-4 rounded ${message.type === "success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Google Form ID</label>
                    <input
                        type="text"
                        name="FORM_ID"
                        value={settings.FORM_ID}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Reference Sheet ID</label>
                    <input
                        type="text"
                        name="REF_SHEET_ID"
                        value={settings.REF_SHEET_ID}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Reference Sheet Tab Name</label>
                    <input
                        type="text"
                        name="REF_SHEET_TAB"
                        value={settings.REF_SHEET_TAB}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Template Document ID</label>
                    <input
                        type="text"
                        name="TEMPLATE_DOC_ID"
                        value={settings.TEMPLATE_DOC_ID}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Output Title Prefix</label>
                    <input
                        type="text"
                        name="OUTPUT_TITLE_PREFIX"
                        value={settings.OUTPUT_TITLE_PREFIX}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Target Folder Name</label>
                    <input
                        type="text"
                        name="FOLDER_NAME"
                        value={settings.FOLDER_NAME}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                    <p className="text-xs text-gray-500 mt-1">Folder will be created if it doesn't exist.</p>
                </div>

                <div className="pt-4">
                    <button
                        type="submit"
                        disabled={saving}
                        className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${saving ? "bg-indigo-400 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700"
                            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
                    >
                        {saving ? "Saving..." : "Save Settings"}
                    </button>
                </div>
            </form>
        </div>
    );
}
