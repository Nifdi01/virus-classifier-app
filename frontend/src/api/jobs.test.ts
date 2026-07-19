import { describe, expect, it } from "vitest";
import { parseSequencesFromFasta } from "./jobs";

describe("parseSequencesFromFasta", () => {
  it("parses multiple FASTA entries and normalizes sequence text", () => {
    const fasta = ">seq1\natgc\ncc\n>seq2\nggtt";

    expect(parseSequencesFromFasta(fasta)).toEqual(["ATGCCC", "GGTT"]);
  });

  it("returns an empty array for empty input", () => {
    expect(parseSequencesFromFasta("")).toEqual([]);
  });
});
