import ROOT

def plot_b_variations():

    # --- Apri il file ---
    f = ROOT.TFile.Open("fit_templates_HHbbtt_good/datacards_reweight/2022_preEE/msd-80to170_Pt-300to350_particleNet_XbbVsQCD-HHbbtt/tau21_0p30/pass/shapes.root")
    if not f or f.IsZombie():
        raise RuntimeError("Errore: file ROOT non aperto")

    # --- Recupera gli istogrammi ---
    h_nom  = f.Get("b_2022_preEE_nominal")
    h_up   = f.Get("b_2022_preEE_QCD_MuEnriched_ratioUp")
    h_down = f.Get("b_2022_preEE_QCD_MuEnriched_ratioDown")

    if not h_nom or not h_up or not h_down:
        raise RuntimeError("Errore: uno o più istogrammi non trovati")

    # --- Niente stats box ---
    ROOT.gStyle.SetOptStat(0)

    # --- Canvas ad alta risoluzione ---
    c = ROOT.TCanvas("c", "", 2000, 1500)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetBottomMargin(0.12)

    # --- Stili ---
    h_nom.SetLineColor(ROOT.kBlack)
    h_nom.SetLineWidth(3)

    h_up.SetLineColor(ROOT.kRed + 1)
    h_up.SetLineWidth(3)
    h_up.SetLineStyle(2)   # tratteggiata

    h_down.SetLineColor(ROOT.kBlue + 1)
    h_down.SetLineWidth(3)
    h_down.SetLineStyle(2) # tratteggiata

    # --- Titoli ---
    h_nom.SetTitle("")
    h_nom.GetXaxis().SetTitle("Observable")
    h_nom.GetYaxis().SetTitle("Events")

    h_nom.GetXaxis().SetTitleSize(0.045)
    h_nom.GetYaxis().SetTitleSize(0.045)
    h_nom.GetXaxis().SetLabelSize(0.04)
    h_nom.GetYaxis().SetLabelSize(0.04)

    # --- Disegno ---
    h_nom.Draw("HIST")
    h_up.Draw("HIST SAME")
    h_down.Draw("HIST SAME")

    # --- Legenda ---
    leg = ROOT.TLegend(0.60, 0.70, 0.88, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.04)

    leg.AddEntry(h_nom,  "Nominal", "l")
    leg.AddEntry(h_up,   "QCD MuEnriched ratio Up", "l")
    leg.AddEntry(h_down, "QCD MuEnriched ratio Down", "l")

    leg.Draw()

    # --- Salva ---
    c.SaveAs("plots/b_2022_preEE_QCD_ratio_comparison.pdf")
    c.SaveAs("plots/b_2022_preEE_QCD_ratio_comparison.png")

    print("Plot salvati correttamente.")

if __name__ == "__main__":
    plot_b_variations()
