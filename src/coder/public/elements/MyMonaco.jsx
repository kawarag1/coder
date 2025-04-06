import React, { useEffect, useRef } from "react";
import { useRecoilValue } from "recoil";
import { callFnState } from "@chainlit/react-client";

export default function MonacoEditorComponent() {
  const editorRef = useRef(null);
  const editorInstanceRef = useRef(null);
  const callFn = useRecoilValue(callFnState);

  useEffect(() => {
    // If the global Monaco object already exists, initialize the editor
    if (window.monaco && window.monaco.editor) {
      initializeEditor();
      return;
    }

    // If the script is already added, wait for its loading
    const existingScript = document.querySelector(
      `script[src^="https://unpkg.com/monaco-editor"]`
    );
    if (existingScript) {
      existingScript.addEventListener("load", initializeMonaco);
      return;
    }

    // If the script is not added yet, dynamically add it
    const script = document.createElement("script");
    script.src = "https://unpkg.com/monaco-editor@0.52.2/min/vs/loader.js";
    script.async = true;
    script.defer = true;
    script.onload = initializeMonaco;
    document.head.appendChild(script);

    function initializeMonaco() {
      // Configure the path to Monaco modules via CDN
      window.require.config({
        paths: { vs: "https://unpkg.com/monaco-editor@0.52.2/min/vs" },
      });
      // Load the main editor module and initialize it
      window.require(["vs/editor/editor.main"], initializeEditor);
    }
  }, []);

  // Example of using callFn to update the editor content
  useEffect(() => {
    if (callFn?.name === "update-editor") {
      const { newValue } = callFn.args;
      if (editorInstanceRef.current && newValue !== undefined) {
        editorInstanceRef.current.setValue(newValue);
      }
      callFn.callback();
    }
  }, [callFn]);

  const initializeEditor = () => {
    if (editorRef.current && !editorInstanceRef.current) {
      editorInstanceRef.current = window.monaco.editor.create(
        editorRef.current,
        {
          value: "function hello() {\n\talert('Hello, world!');\n}",
          language: "python",
          theme: "vs-dark",
        }
      );
    }
  };

  return (
    <div className="h-full w-full relative">
      <div ref={editorRef} className="h-full w-full" />
    </div>
  );
}
