function sanitizeFileNamePart(value: string): string {
  return value.replace(/[^a-zA-Z0-9-_]+/g, "_");
}

export function downloadTextArtifact(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

export function printTextArtifact(title: string, content: string): void {
  const escapedContent = content
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
  const printWindow = window.open("", "_blank", "width=900,height=700");
  if (!printWindow) {
    return;
  }
  printWindow.document.write(`
    <html>
      <head>
        <title>${title}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 24px; line-height: 1.5; }
          h1 { margin-bottom: 12px; }
          pre { white-space: pre-wrap; font-size: 14px; }
        </style>
      </head>
      <body>
        <h1>${title}</h1>
        <pre>${escapedContent}</pre>
      </body>
    </html>
  `);
  printWindow.document.close();
  printWindow.focus();
  printWindow.print();
}

export function buildPrescriptionArtifactContent(input: {
  clinicName: string;
  prescriptionId: number;
  appointmentId: number;
  doctorName: string;
  diagnosis: string | null;
  medicines: string | null;
  dosage: string | null;
  frequency: string | null;
  duration: string | null;
  doctorAdvice: string | null;
  followUpDate: string | null;
  issuedAt: string | null;
}): string {
  return [
    input.clinicName,
    "Prescription Summary",
    "---------------------",
    `Prescription ID: ${input.prescriptionId}`,
    `Appointment ID: ${input.appointmentId}`,
    `Doctor: ${input.doctorName}`,
    `Issued At: ${input.issuedAt ?? "N/A"}`,
    "",
    `Diagnosis: ${input.diagnosis ?? "N/A"}`,
    `Medicines: ${input.medicines ?? "N/A"}`,
    `Dosage: ${input.dosage ?? "N/A"}`,
    `Frequency: ${input.frequency ?? "N/A"}`,
    `Duration: ${input.duration ?? "N/A"}`,
    `Doctor Advice: ${input.doctorAdvice ?? "N/A"}`,
    `Follow-up Date: ${input.followUpDate ?? "N/A"}`
  ].join("\n");
}

export function buildBookingConfirmationArtifactContent(input: {
  clinicName: string;
  appointmentId: number;
  patientPhone: string;
  doctorName: string;
  date: string;
  startTime: string;
  endTime: string;
  status: string;
  bookingSource: string | null;
}): string {
  return [
    input.clinicName,
    "Appointment Confirmation",
    "------------------------",
    `Appointment ID: ${input.appointmentId}`,
    `Patient Phone: ${input.patientPhone}`,
    `Doctor: ${input.doctorName}`,
    `Date: ${input.date}`,
    `Slot: ${input.startTime} - ${input.endTime}`,
    `Status: ${input.status}`,
    `Source: ${input.bookingSource ?? "N/A"}`,
    "",
    "Please arrive 10 minutes before your scheduled slot."
  ].join("\n");
}

export function bookingConfirmationFileName(appointmentId: number): string {
  return `appointment_confirmation_${sanitizeFileNamePart(String(appointmentId))}.txt`;
}

export function prescriptionFileName(prescriptionId: number): string {
  return `prescription_${sanitizeFileNamePart(String(prescriptionId))}.txt`;
}
