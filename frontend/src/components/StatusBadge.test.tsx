import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import StatusBadge from "./StatusBadge";
import type { CeleryStatus } from "../types/job";

const statusCases: {
  status: CeleryStatus;
  label: string;
  className: string;
}[] = [
  { status: "SUCCESS", label: "complete", className: "bg-green-100" },
  { status: "FAILURE", label: "failed", className: "bg-red-100" },
  { status: "PROGRESS", label: "running", className: "bg-amber-100" },
  { status: "PENDING", label: "queued", className: "bg-gray-100" },
];

describe("StatusBadge", () => {
  for (const { status, label, className } of statusCases) {
    it(`renders ${status} with expected label and style`, () => {
      const html = renderToStaticMarkup(<StatusBadge status={status} />);

      expect(html).toContain(label);
      expect(html).toContain(className);
    });
  }
});
