import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { AIInsightPanel } from "@/components/common/AIInsightPanel";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import {
  Mic,
  MicOff,
  Upload,
  CheckCircle2,
  AlertTriangle,
  MapPin,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  FileText,
  Shield,
  Layers,
  Building,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function SubmitGrievancePage() {
  const navigate = useNavigate();

  // Wizard Step (1 to 5)
  const [currentStep, setCurrentStep] = useState(1);

  // Form Fields
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [language, setLanguage] = useState<"en" | "hi" | "hinglish">("en");
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // Location
  const [address, setAddress] = useState("Pocket 4, Gate 2, Vasant Kunj, New Delhi");
  const [ward, setWard] = useState("Ward 14 (South Zone)");
  const [zone, setZone] = useState("South Zone");
  const [lat, setLat] = useState(28.5244);
  const [lng, setLng] = useState(77.1558);

  // Category
  const [category, setCategory] = useState("Water Supply & Sanitation");
  const [subcategory, setSubcategory] = useState("Pipeline Rupture & Leakage");
  const [manualCategoryOverride, setManualCategoryOverride] = useState(false);

  // Evidence
  const [files, setFiles] = useState<Array<{ name: string; size: string; type: "image" | "document" }>>([]);

  // AI Inference State
  const [aiAnalyzing, setAiAnalyzing] = useState(false);
  const [aiResult, setAiResult] = useState<any>(null);
  const [dismissDuplicateAlert, setDismissDuplicateAlert] = useState(false);

  // Submitting state
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Trigger AI analysis when description is filled
  const handleAnalyzeAI = async () => {
    if (!description || description.length < 15) return;
    setAiAnalyzing(true);
    const res = await grievanceService.analyzeWithAI(description, address);
    setAiResult(res);
    if (!manualCategoryOverride) {
      setCategory(res.predictedCategory);
      setSubcategory(res.predictedSubcategory);
    }
    if (!title) {
      setTitle(res.summary);
    }
    setAiAnalyzing(false);
  };

  // Mock voice recorder simulation
  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      setTimeout(() => {
        setDescription(
          "Main feeder pipe line burst near Community Center Gate 2. Paani bahut tez beh raha hai and road collapse hone ka risk hai."
        );
        setIsRecording(false);
        handleAnalyzeAI();
      }, 2500);
    } else {
      setIsRecording(false);
    }
  };

  // Mock file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFiles((prev) => [
        ...prev,
        {
          name: file.name,
          size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
          type: file.type.startsWith("image/") ? "image" : "document",
        },
      ]);
    }
  };

  const handleFinalSubmit = async () => {
    setIsSubmitting(true);
    const created = await grievanceService.create({
      title: title || "Citizen Grievance",
      description,
      language,
      isAnonymous,
      category,
      subcategory,
      location: {
        address,
        ward,
        zone,
        lat,
        lng,
      },
      priority: aiResult?.priority || "medium",
      aiConfidence: aiResult?.confidence || 0.94,
      duplicateProbability: aiResult?.duplicateProbability || 0.05,
      evidence: files.map((f, i) => ({
        id: `ev_${Date.now()}_${i}`,
        name: f.name,
        size: f.size,
        type: f.type,
        url: "https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&auto=format&fit=crop&q=80",
      })),
    });

    setIsSubmitting(false);
    navigate(`/citizen/grievances/${created.id}?success=true`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title="File a Citizen Grievance"
        subtitle="Submit your issue with automated AI assistance, duplicate detection, and direct department dispatch."
        breadcrumbs={[
          { label: "Citizen Portal", href: "/citizen/dashboard" },
          { label: "Complaint Submission Wizard", active: true },
        ]}
      />

      {/* Step Progress Tracker */}
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle">
        <div className="flex items-center justify-between text-xs font-semibold">
          {[
            { step: 1, label: "Description & AI" },
            { step: 2, label: "Geographic Location" },
            { step: 3, label: "Category & Dept" },
            { step: 4, label: "Evidence Attachments" },
            { step: 5, label: "Review & Submit" },
          ].map((s) => (
            <div
              key={s.step}
              className={cn(
                "flex items-center gap-2",
                currentStep === s.step
                  ? "text-blue-600 font-bold"
                  : currentStep > s.step
                  ? "text-emerald-600 font-medium"
                  : "text-slate-400"
              )}
            >
              <div
                className={cn(
                  "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border transition-colors",
                  currentStep === s.step
                    ? "bg-blue-600 text-white border-blue-600 shadow-xs"
                    : currentStep > s.step
                    ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                    : "bg-slate-100 text-slate-400 border-slate-200"
                )}
              >
                {currentStep > s.step ? "✓" : s.step}
              </div>
              <span className="hidden sm:inline">{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* STEP 1: Description & AI */}
      {currentStep === 1 && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-subtle space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Step 1: Complaint Description</h3>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-medium">Input Language:</span>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as any)}
                className="text-xs border border-slate-200 rounded px-2 py-1 bg-white font-medium text-slate-700"
              >
                <option value="en">English</option>
                <option value="hi">Hindi (हिंदी)</option>
                <option value="hinglish">Hinglish</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Issue Summary / Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Broken water pipeline leaking on pavement..."
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold text-slate-700">
                Detailed Statement of Grievance
              </label>
              <button
                type="button"
                onClick={toggleRecording}
                className={cn(
                  "inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border transition-colors",
                  isRecording
                    ? "bg-red-50 text-red-700 border-red-300 animate-pulse"
                    : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                )}
              >
                {isRecording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5 text-blue-600" />}
                {isRecording ? "Listening (Speaking in Hindi/English)..." : "Voice Input (Speech-to-Text)"}
              </button>
            </div>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onBlur={handleAnalyzeAI}
              placeholder="Please provide full details of the issue, severity, duration, and any immediate hazards..."
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <div className="flex items-center justify-between mt-1 text-[11px] text-slate-400">
              <span>Type your complaint in plain English, Hindi or Hinglish.</span>
              <button
                type="button"
                onClick={handleAnalyzeAI}
                disabled={aiAnalyzing || !description}
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                {aiAnalyzing ? "Running NLP Engine..." : "Run AI Analysis Now →"}
              </button>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded border border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-slate-500" />
              <div>
                <span className="text-xs font-semibold text-slate-900 block">Anonymous Filing</span>
                <span className="text-[11px] text-slate-500">Your identity will be masked from field staff.</span>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* AI Analysis Panel */}
          {aiResult && (
            <div className="pt-2">
              <AIInsightPanel
                predictionResult={aiResult}
                onOverride={() => {
                  setManualCategoryOverride(true);
                  setCurrentStep(3);
                }}
              />
            </div>
          )}

          {/* Duplicate Warning Box */}
          {aiResult?.similarComplaints?.length > 0 && !dismissDuplicateAlert && (
            <div className="p-4 rounded-md bg-amber-50 border border-amber-200 space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                  <span className="text-xs font-bold text-amber-900">
                    Existing Similar Grievance Detected Nearby
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setDismissDuplicateAlert(true)}
                  className="text-[11px] text-slate-500 hover:text-slate-700 underline"
                >
                  Dismiss warning
                </button>
              </div>

              <p className="text-xs text-amber-800 leading-relaxed">
                Our semantic engine detected a pending complaint matching this incident in your ward. You can view its current progress or proceed if this is a separate occurrence:
              </p>

              <div className="space-y-2">
                {aiResult.similarComplaints.map((item: any) => (
                  <div
                    key={item.id}
                    className="p-2.5 bg-white rounded border border-amber-200/80 flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-800">{item.id}</span>
                        <span className="font-mono text-emerald-700 font-semibold bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                          {Math.round(item.similarity * 100)}% match
                        </span>
                      </div>
                      <p className="text-slate-700 font-medium mt-0.5">{item.title}</p>
                    </div>

                    <a
                      href={`/citizen/grievances/${item.id}`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-blue-600 hover:underline font-semibold"
                    >
                      Track Existing →
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end pt-3">
            <button
              type="button"
              disabled={!description}
              onClick={() => setCurrentStep(2)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded text-xs font-semibold shadow-subtle transition-colors"
            >
              Continue to Location <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Location */}
      {currentStep === 2 && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-subtle space-y-5">
          <h3 className="text-sm font-bold text-slate-900">Step 2: Geographic Location</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Street Address / Landmark
              </label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Municipal Ward
              </label>
              <select
                value={ward}
                onChange={(e) => setWard(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="Ward 14 (South Zone)">Ward 14 (Vasant Kunj)</option>
                <option value="Ward 15 (South Zone)">Ward 15 (Outer Ring Road)</option>
                <option value="Ward 07 (Central Zone)">Ward 07 (Karol Bagh)</option>
                <option value="Ward 12 (West Zone)">Ward 12 (Dwarka)</option>
                <option value="Ward 18 (West Zone)">Ward 18 (Tilak Nagar)</option>
                <option value="Ward 22 (East Zone)">Ward 22 (Mayur Vihar)</option>
              </select>
            </div>
          </div>

          {/* Interactive Map Picker Representation */}
          <div className="rounded-md border border-slate-200 overflow-hidden bg-slate-900 p-4 text-white relative h-64 flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold flex items-center gap-1.5 text-blue-300">
                <MapPin className="w-4 h-4 text-red-500 animate-bounce" />
                GPS Coordinates Pin: [{lat.toFixed(4)}, {lng.toFixed(4)}]
              </span>
              <span className="text-[10px] font-mono bg-blue-900/60 text-blue-200 px-2 py-0.5 rounded">
                Click map to reposition pin
              </span>
            </div>

            <div
              className="flex-1 my-3 rounded bg-[#0b132b] relative cursor-crosshair flex items-center justify-center border border-slate-800"
              onClick={(e) => {
                // Mock coordinate update on click
                setLat((prev) => prev + (Math.random() - 0.5) * 0.005);
                setLng((prev) => prev + (Math.random() - 0.5) * 0.005);
              }}
            >
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:2rem_2rem] opacity-30" />
              <div className="w-4 h-4 rounded-full bg-red-500 ring-4 ring-red-400/30 flex items-center justify-center text-white text-[10px] font-bold z-10 shadow-lg">
                ●
              </div>
              <span className="absolute bottom-2 left-2 text-[10px] font-mono text-slate-400">
                Selected: {address}
              </span>
            </div>

            <div className="text-[11px] text-slate-400 flex items-center justify-between">
              <span>Zone: {zone}</span>
              <span className="text-emerald-400">● Field Geofence Verified</span>
            </div>
          </div>

          <div className="flex justify-between pt-3">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border border-slate-200 text-slate-700 rounded text-xs font-medium hover:bg-slate-50"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle"
            >
              Continue to Category <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Category and Department */}
      {currentStep === 3 && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-subtle space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Step 3: Category & Department Routing</h3>
            <span className="text-xs text-blue-600 font-mono font-semibold">
              AI Predicted: {category}
            </span>
          </div>

          <div className="p-3.5 bg-blue-50/70 rounded-md border border-blue-200 flex items-start gap-3 text-xs text-blue-900">
            <Sparkles className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Automated Dispatch Assignment</span>
              <p className="mt-0.5 text-blue-800 leading-snug">
                Our NLP model pre-selected this department based on your description. If you believe this is incorrect, you can manually override it below.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Department
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 font-medium"
              >
                <option value="Water Supply & Sanitation">Water Supply & Sewerage Board (WSSB)</option>
                <option value="Roads & Traffic Infrastructure">Public Works Department (PWD Roads)</option>
                <option value="Solid Waste Management">Solid Waste Management (SWM)</option>
                <option value="Electricity & Street Lighting">Urban Electricity & Street Lighting</option>
                <option value="Public Health & Sanitation">Public Health & Vector Control</option>
                <option value="Parks & Horticulture">Horticulture & Public Parks</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Subcategory
              </label>
              <input
                type="text"
                value={subcategory}
                onChange={(e) => setSubcategory(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 font-medium"
              />
            </div>
          </div>

          <div className="flex justify-between pt-3">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border border-slate-200 text-slate-700 rounded text-xs font-medium hover:bg-slate-50"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle"
            >
              Continue to Evidence <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Evidence Upload */}
      {currentStep === 4 && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-subtle space-y-5">
          <h3 className="text-sm font-bold text-slate-900">Step 4: Evidence Uploads</h3>
          <p className="text-xs text-slate-500">
            Upload photographs, video clips, or PDF documents to help field inspectors verify the issue quickly.
          </p>

          {/* Drag & Drop Upload Zone */}
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors bg-slate-50/50">
            <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <p className="text-xs font-semibold text-slate-700">
              Drag and drop files here, or browse
            </p>
            <p className="text-[11px] text-slate-400 mt-1">
              Supports JPG, PNG, PDF, MP4 up to 25MB each
            </p>
            <label className="mt-3 inline-block">
              <span className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 rounded text-xs font-semibold hover:bg-slate-100 cursor-pointer shadow-subtle">
                Choose Local File
              </span>
              <input
                type="file"
                className="hidden"
                accept="image/*,application/pdf"
                onChange={handleFileUpload}
              />
            </label>
          </div>

          {/* Attached Files List */}
          {files.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-700">Attached Documents ({files.length})</span>
              {files.map((f, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-2.5 bg-slate-50 rounded border border-slate-200 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-slate-800">{f.name}</span>
                    <span className="text-slate-400 font-mono text-[10px]">({f.size})</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setFiles(files.filter((_, idx) => idx !== i))}
                    className="text-red-600 hover:text-red-800 text-xs font-medium"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex justify-between pt-3">
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border border-slate-200 text-slate-700 rounded text-xs font-medium hover:bg-slate-50"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(5)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle"
            >
              Review & Finalize <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: Review and Submission */}
      {currentStep === 5 && (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-subtle space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">Step 5: Review Grievance Details</h3>
            <span className="text-xs font-mono text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Ready to Dispatch
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="bg-slate-50 p-3.5 rounded border border-slate-200">
              <span className="text-slate-400 uppercase font-mono text-[10px] block">Title</span>
              <p className="font-semibold text-slate-900 mt-1">{title || "Civic Complaint"}</p>
            </div>

            <div className="bg-slate-50 p-3.5 rounded border border-slate-200">
              <span className="text-slate-400 uppercase font-mono text-[10px] block">Department & Category</span>
              <p className="font-semibold text-slate-900 mt-1">{category} • {subcategory}</p>
            </div>

            <div className="bg-slate-50 p-3.5 rounded border border-slate-200">
              <span className="text-slate-400 uppercase font-mono text-[10px] block">Geographic Location</span>
              <p className="font-semibold text-slate-900 mt-1">{address} ({ward})</p>
            </div>

            <div className="bg-slate-50 p-3.5 rounded border border-slate-200">
              <span className="text-slate-400 uppercase font-mono text-[10px] block">Citizen Privacy</span>
              <p className="font-semibold text-slate-900 mt-1">
                {isAnonymous ? "Anonymous Submission" : "Aarav Sharma (Verified Citizen)"}
              </p>
            </div>
          </div>

          <div>
            <span className="text-xs font-semibold text-slate-700 block mb-1">Statement</span>
            <div className="p-3.5 bg-slate-50 rounded border border-slate-200 text-xs text-slate-700 whitespace-pre-wrap leading-relaxed">
              {description}
            </div>
          </div>

          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded text-xs text-emerald-900 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>
              By submitting, your grievance will be registered on the immutable audit ledger and assigned directly to the field engineering crew with an auto-calculated SLA deadline.
            </span>
          </div>

          <div className="flex justify-between pt-3">
            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border border-slate-200 text-slate-700 rounded text-xs font-medium hover:bg-slate-50"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back
            </button>
            <button
              type="button"
              disabled={isSubmitting}
              onClick={handleFinalSubmit}
              className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded text-xs font-bold shadow-subtle transition-colors"
            >
              {isSubmitting ? "Transmitting to Civic AI Router..." : "Confirm & Submit Grievance →"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
