#!/usr/bin/env python3
"""Generate docs/EXTERNALITY.md - the externality expense economy.

An argument page: it proposes a fiscal instrument and says what would make it wrong.
Its factual premises are read from pinned documents, and every statement is a
checked claim (LIVE_NUMBERS.md section 11), registered in
data/manual/claims.d/w3-le.json with what it rests on. What the page once said and
could not justify is in docs/ARCHIVE.md, not here.

    python3 scripts/pages/externality.py

Writes docs/EXTERNALITY.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import ROOT, log, write_doc
import claims as _claims
import live

OUT = os.path.join(ROOT, "docs", "EXTERNALITY.md")
C, B, E = live.claim, live.claim_begin, live.CLAIM_END
_REG = {}


def _cl():
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _REG["d"]


def RD(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase. Each reading has its own phrase."""
    d = _cl()
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def render():
    t_lo = RD("LE-MST-TURF-2018", 100, "omkring 100-120 tons")
    t_hi = RD("LE-MST-TURF-2018", 120, "100-120 tons gummigranulat")
    reach_y = RD("LE-EEB-REACH-2026", 5, "it took authorities 5 years and seven months to adopt a restriction")

    o = []
    w = o.append
    w("# The externality expense economy")
    w("")
    w(C("C-LE-E-KIND", "**This page is an argument, not a finding.** It proposes a fiscal "
        "instrument, works out what it would do to the products it applies to, and states what "
        "would make it wrong. Nothing in it is measured by this project, and it is kept out of "
        "the investigation pages for that reason.") + " "
      + C("C-LE-E-PART", "It belongs to the same part of the project as "
          "[the programme](PROGRAMME.md): what ought to be done, labelled as such."))
    w("")
    w(C("C-LE-E-THREE", "It is here because three separate arguments elsewhere in this project "
        "all end at the same missing piece."))
    w("")
    w("- " + C("C-LE-E-A1", "[Section 4](PROGRAMME.md) says a novo-chemical has to be "
               "**destroyed**, and destruction is a cost nobody is obliged to pay."))
    w("- " + C("C-LE-E-A2", "[The industry question](PROGRAMME.md) says the demand for "
               "destruction is currently liability demand — courts, after the fact, in another "
               "country."))
    w("- " + C("C-LE-E-A3", "[The REACH row](PROGRAMME.md) says a product ban is harmonised at EU "
               "level, so no city, region or utility can start one."))
    w("")
    w(C("C-LE-E-LEVY", "A levy is none of those things. It is a national fiscal instrument, it "
        "applies before the harm rather than after it, and it is the lever that stays available "
        "when market access is closed off."))
    w("")
    w("---")
    w("")
    w("## The model, in five clauses")
    w("")
    w("1. " + C("C-LE-E-CL1", "**A product carries a levy at purchase, sized to its pollutive "
                "potential** — and covering only a fraction of it."))
    w("2. " + C("C-LE-E-CL2", "**The buyer holds a return obligation:** hand the object back for "
                "destruction or recovery *before it deteriorates past the point where it can be "
                "collected*. Fabric before it is fibre, pellets before they are micro, micro before "
                "nano."))
    w("3. " + C("C-LE-E-CL3", "**Return in time and the fraction was the whole price.** The levy "
                "behaves as a deposit, not a tax."))
    w("4. " + C("C-LE-E-CL4", "**Fail to return and the buyer is billed the full externality, "
                "computed non-conservatively** — the upper estimate, not the cautious one."))
    w("5. " + C("C-LE-E-CL5", "**The supplier is fined for having sold to a buyer who did not "
                "return it.**"))
    w("")
    w("### Why the shape matters more than the rate")
    w("")
    w(C("C-LE-E-AMBIG", "**It prices ambiguity against whoever can resolve it.** Non-conservative "
        "billing inverts the usual burden. An unreturned object is assumed to have done its "
        "worst, and the only way to rebut that assumption is to produce the object — which is "
        "exactly what the person holding it can do and nobody else can.") + " "
      + C("C-LE-E-BAN", "A ban or a liability claim, by contrast, needs a regulator or a court to "
          "show a harm that is diffuse by construction."))
    w("")
    w(C("C-LE-E-DEPOSIT", "**It is a deposit, so it is revenue-neutral for the compliant.** That "
        "changes the political argument it has to win. A tax is fought on whether the state "
        "should have the money. A deposit is fought on whether you intend to bring the thing "
        "back, which is a much worse position to defend from."))
    w("")
    w(C("C-LE-E-DEMAND", "**It supplies the demand curve that destruction capacity does not "
        "have.** The unmanaged price exceeds the managed price by construction, at a ratio the "
        "levy sets. That is the piece the industry argument is missing: not a subsidy, not a "
        "court award years later, but a price on the day."))
    w("")
    w(C("C-LE-E-CONTRAST", "**It generates the contrast this project keeps saying nobody "
        "created.** Levies are set by states, rates differ, municipalities can add return "
        "infrastructure or not — so places differ, on dates, in a recorded way. That is "
        "[the plurality argument](PLACES.md) arriving through the tax code instead of through a "
        "trial protocol."))
    w("")
    w("---")
    w("")
    w("## Leasing is the wrapper, and it already exists")
    w("")
    w(C("C-LE-E-FINE", "The supplier fine is the clause that does the structural work, because "
        "the cheapest way to avoid being fined for your buyer is **not to have one.** Keep title, "
        "rent the product, carry the return obligation yourself.") + " "
      + C("C-LE-E-LEASE", "The instrument for that is a lease, and leasing is not a new legal form "
          "that has to be invented for this: it is ordinary contract law, in which the lessor "
          "stays the legal owner and the lessee obtains the right to use the asset, with "
          "liability, condition on return and remedies set in the contract."))
    w("")
    w(C("C-LE-E-MANDATE", "So the precedent is in the **instrument** and it is missing in the "
        "**mandate**. Nobody has to invent a legal vehicle to make a pollutive product "
        "returnable. What this page has not found is a rule that says *this kind of chemistry "
        "may only be placed on the market under a return-bearing title*. Denmark already runs a "
        "deposit system for drinks containers, EU law already makes producers finance the "
        "collection and treatment of electronics and batteries, and a lease already keeps title "
        "with the lessor. The gap is that none of them is keyed to what the substance does when "
        "it disperses."))
    w("")
    w(C("C-LE-E-PRIOR", "That gap is where the design decision sits, and it is a small one to "
        "state and a large one to legislate: **the levy class should be keyed to the "
        "evolutionary prior**, the same taxonomy [section 5](PROGRAMME.md) uses for source "
        "control. A substance life has met before has a concentration below which return is not "
        "worth compelling. A substance with no prior that never degrades has no such level, and "
        "it is the case where non-conservative billing does all the work."))
    w("")
    w("---")
    w("")
    w("## Four classes, and what the model does to each")
    w("")
    w(C("C-LE-E-EXAMPLES", "The examples are not decorative. They mark where the model works as "
        "written, where it degrades into something weaker, and where it stops being applicable "
        "— and a proposal that cannot say where it stops is not a proposal."))
    w("")
    w("### A — Returnable and identifiable: the model works as written")
    w("")
    w("| Product | Why it fits | What changes |")
    w("|---|---|---|")
    w("| **Artificial turf pitches** | "
      + C("C-LE-E-TURF", f"{t_lo}–{t_hi} t of rubber granulate as infill on an ordinary Danish "
          "football pitch, part of which leaves the pitch for the surroundings and has to be "
          "replaced") + "; "
      + C("C-LE-E-TURF-BUYER", "one buyer, one contract, one supplier") + " | "
      + C("C-LE-E-TURF-EFFECT", "The fine lands on a supplier who sold to a club with no "
          "containment plan. Pitches become leased systems with a contracted end of life") + " |")
    w("| **Agricultural film and silage wrap** | "
      + C("C-LE-E-FILM-FIT", "Farm-level buyer, dealer-level supplier, field-scale plastic on "
          "exactly the deterioration schedule the model is built around") + " | "
      + C("C-LE-E-FILM-EFFECT", "Dealers become collection points; thicker reusable covers and "
          "returnable silos beat single-use film on total cost") + " |")
    w("| **Batteries and electronics** | "
      + C("C-LE-E-BATT-FIT", "Already under producer responsibility") + " | "
      + C("C-LE-E-BATT-EFFECT", "Nothing structural — the mechanism exists, and what producers "
          "are made to finance is collection and treatment, not the externality. This is the "
          "precedent, not the frontier") + " |")
    w("| **Nets, ropes, dolly rope** | "
      + C("C-LE-E-NETS-FIT", "Ghost gear *is* the unreturned item") + " | "
      + C("C-LE-E-NETS-EFFECT", "Gear becomes an asset on a register rather than a consumable")
      + " |")
    w("")
    w("### B — Disperses during use: return cannot catch it")
    w("")
    w(C("C-LE-E-TYRES", "**Tyres** are the clean case. The worn tyre is an object that can be "
        "handed back; the wear left on the road while driving is the externality, and no return "
        "obligation reaches it. So the levy cannot be a deposit here — it has to be sized to the "
        "**wear fraction** and hypothecated to capture: ponds, gully traps, street sweeping. "
        "Which is this project's [pond argument](PROGRAMME.md) arriving from the fiscal side, and "
        "it is the same money."))
    w("")
    w(C("C-LE-E-ABRASION", "The supply effect is not on the return channel but on the product: "
        "**abrasion becomes a priced attribute**.") + " "
      + C("C-LE-E-TYRELABEL", "The EU tyre label already grades rolling resistance and wet grip, "
          "and the labelling regulation empowers the Commission to add abrasion once reliable "
          "test methods exist.") + " "
      + C("C-LE-E-SAMECLASS", "Brake pads, antifouling paint and ski wax sit in the same class, "
          "and for them the honest reduction is a use restriction plus a hypothecated levy rather "
          "than a deposit."))
    w("")
    w("### C — Atomised consumables: identification fails")
    w("")
    w(C("C-LE-E-ATOMISED", "Cigarette filters, wipes, glitter, sachets. There is nothing to "
        "return and nobody to bill, so the model collapses to a plain levy plus the supplier fine "
        "— a weaker instrument, and worth admitting as one. The only real lever left is "
        "**format**: refill, concentrate, dispenser, deposit-bearing container. The accountable "
        "party becomes the retailer, because the retailer is the last identifiable person in the "
        "chain."))
    w("")
    w("### D — A novo-chemical inside a returnable product: the interesting case")
    w("")
    w(C("C-LE-E-PFAS", "A PFAS jacket comes back. The PFAS left during use and does not "
        "degrade.") + " "
      + C("C-LE-E-RESERVED", "Non-conservative billing on that residue is effectively prohibitive "
          "— which means **the model delivers reserved use by price rather than by ban.** That is "
          "the outcome [section 5](PROGRAMME.md) argues for and [the REACH row](PROGRAMME.md) "
          "says no city may impose."))
    w("")
    w(C("C-LE-E-DECLARE", "And it has a second effect that is better than the first. A supplier "
        "who declares a product free of the substance pays no levy — and is liable if the "
        "declaration is wrong. **That converts a marketing claim into a fiscal declaration**, "
        "dated and auditable the way a tax return is."))
    w("")
    w("---")
    w("")
    w("## What it does to the supply landscape")
    w("")
    w(C("C-LE-E-SUPPLY-INTRO", "This is the part worth thinking through, because a levy that only "
        "changed prices would be a rounding error. What it changes is what kinds of firms can "
        "operate."))
    w("")
    w(C("C-LE-E-SERVICES", "**Products become services wherever return matters.** Not as an "
        "aspiration — as the cheapest available defence against the supplier fine. Pitch "
        "systems, film, workwear, protective clothing, equipment: the firms that keep title stop "
        "being exposed to their customers' behaviour. Ownership becomes the expensive way to sell "
        "a dispersing product."))
    w("")
    w(C("C-LE-E-MONO", "**Mono-material and repairable design wins on cost, not on virtue.** A "
        "returned object has recovery value only if it can be taken apart; a blended textile and "
        "a bonded assembly are worth less at return than they cost to process. The levy makes "
        "that difference visible at the point of design instead of at the end of life."))
    w("")
    w(C("C-LE-E-VARIETY", "**Variety collapses where return channels are expensive, and that is a "
        "real cost.** Every product variant needs its own return path, so the model penalises "
        "catalogue proliferation. Some of that is pure gain — fewer, longer-lived, "
        "better-specified products. Some of it is consolidation: a small supplier cannot carry "
        "unbounded liability alone, so **without a pooled compliance scheme this instrument "
        "concentrates the market**, which is an objection the design has to answer rather than an "
        "incidental effect."))
    w("")
    w(C("C-LE-E-INSURANCE", "**Insurance enters, and becomes the fast regulator.** Unbounded "
        "liability is exactly what an insurance market prices, and an insurer that underwrites "
        "return-failure will price chemistry directly: cheaper premiums for substances that "
        "degrade, punitive ones for those that do not. **That is a private regulator that can "
        "reprice at each renewal rather than wait the years a REACH restriction takes** — and it "
        "arrives through a member state's tax code rather than through the harmonised market, "
        "which is the whole point of choosing a fiscal instrument.") + " "
      + C("C-LE-E-REACHYEARS", f"On the European Environmental Bureau's count, in the few years "
          f"before the EU's 2020 chemicals strategy authorities took {reach_y} years and seven "
          "months on average to adopt a REACH restriction."))
    w("")
    w(C("C-LE-E-SECONDHAND", "**Second-hand markets formalise instead of dying.** The obligation "
        "transfers with title, deposit and all, which turns resale into a recorded change of "
        "custody. Durable goods gain; the disposal-by-resale route closes."))
    w("")
    w(C("C-LE-E-IMPORTS", "**Imports are reachable.** A levy falls on imported goods as on "
        "domestic ones: an importer posts the liability or does not place the goods."))
    w("")
    w(C("C-LE-E-FASHION", "**And fast fashion breaks first**, which is worth stating plainly "
        "rather than leaving as an implication. Its unit economics depend on garments not coming "
        "back. A model that prices non-return removes the assumption the business rests on — and "
        "the firms that already run take-back, rental and repair are advantaged by an instrument "
        "they are already paying for voluntarily."))
    w("")
    w("---")
    w("")
    w("## What would make this wrong")
    w("")
    w(C("C-LE-E-VALUATION", "**The valuation is the whole instrument, and it is contestable.** "
        "\"Non-conservative externality\" is a number somebody has to compute, and by this "
        "project's own standard a number nobody can recompute is not a number. The method has to "
        "be published, versioned, and applied to the substance rather than to the industry. "
        "Without that, the model is an invitation to arbitrary billing and would deserve to lose "
        "in court."))
    w("")
    w(C("C-LE-E-RUIN", "**Ruin and regressivity.** A household billed the full non-conservative "
        "externality of a sofa is a headline, not a policy. Three answers exist — a cap, "
        "mandatory insurance, or return infrastructure so easy that failure is a genuine choice — "
        "and only the third leaves the mechanism intact, because the other two re-cap the thing "
        "the model exists to uncap. That makes convenient return a **precondition** of the "
        "instrument rather than an accompaniment to it."))
    w("")
    w(C("C-LE-E-LAUNDER", "**Laundering routes.** Resale without transfer, \"lost\", \"stolen\", "
        "export. The supplier fine is what makes designing against these the supplier's problem, "
        "but each needs a written rule.") + " "
      + C("C-LE-E-EXPORT", "Deposit systems already meet the export route: German supermarkets "
          "near the Danish border exempt Scandinavian residents from the deposit if they sign an "
          "export declaration."))
    w("")
    w(C("C-LE-E-HAZARD", "**The mirror of the moral hazard in the industry argument.** An "
        "industry paid to receive returns acquires an interest in returns being made, which is "
        "benign; an industry paid out of failure-to-return acquires an interest in failure, which "
        "is not. The revenue from the fourth clause must not fund the party that administers the "
        "second clause.") + " "
      + C("C-LE-E-DRS", "Denmark's own deposit operator is funded in part by the deposits on "
          "bottles that are not returned,") + " "
      + C("C-LE-E-DRS-POINT", "so the Danish system already carries the incentive this rule is "
          "meant to prevent."))
    w("")
    w(C("C-LE-E-NOTCOSTED", "**And the honest one: this has not been costed.** No levy rate is "
        "proposed here, no elasticity is estimated, and no Danish legal opinion has been taken on "
        "whether the fifth clause survives contact with proportionality. The argument is that the "
        "*shape* is right — a deposit with an uncapped tail, keyed to what a substance does when "
        "it disperses, wrapped in a lease. The rate, the register and the law are work that has "
        "not been done."))
    w("")
    w("---")
    w("")
    w("## Where it connects")
    w("")
    w("| This page says | Which answers |")
    w("|---|---|")
    w("| A levy is a national fiscal instrument | "
      + C("C-LE-E-W1", "[the REACH row](PROGRAMME.md): a product ban is harmonised, so no level "
          "below the EU can start one") + " |")
    w("| Unmanaged dispersal costs more than managed destruction, on the day | "
      + C("C-LE-E-W2", "[the industry question](PROGRAMME.md): destruction has liability demand "
          "and no market demand") + " |")
    w("| The levy class is keyed to the evolutionary prior | "
      + C("C-LE-E-W3", "[section 5](PROGRAMME.md): the same taxonomy already decides the "
          "source-control instrument and the disposal route") + " |")
    w("| Rates and return infrastructure differ by place, on dates | "
      + C("C-LE-E-W4", "[the plurality argument](PLACES.md): difference between places is what "
          "makes any of this identifiable") + " |")
    return "\n".join(o).rstrip("\n") + "\n"


def main(argv):
    try:
        write_doc(OUT, render())
    except (live.Unjustified, _claims.Refused) as e:
        log(str(e))
        return 1
    log("wrote docs/EXTERNALITY.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
