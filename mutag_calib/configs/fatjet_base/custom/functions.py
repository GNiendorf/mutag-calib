import numpy as np
import awkward as ak
from pocket_coffea.lib.cut_definition import Cut

def tagger_mask(events, params, **kwargs):
    mask = np.zeros(len(events), dtype='bool')
    for tagger in params["taggers"]:
        mask = mask | (events.FatJetGood[:,0][tagger] > params["wp"])
    assert (params["category"] in ["pass", "fail"]), "The allowed categories for the tagger selection are 'pass' and 'fail'"
    if params["category"] == "fail":
        mask = ~mask
    return mask

def tagger_pass(events, params, **kwargs):
    mask = np.zeros(len(events), dtype='bool')
    for tagger in params["taggers"]:
        mask = mask | (events.FatJetGood[:,0][tagger] > params["wp"])

    return mask

def tagger_fail(events, params, **kwargs):
    mask = np.zeros(len(events), dtype='bool')
    for tagger in params["taggers"]:
        mask = mask | (events.FatJetGood[:,0][tagger] < params["wp"])

    return mask

def tagger_mask_exclusive_wp(events, params, **kwargs):
    assert (len(params["wp"]) == 2), "The 'wp' parameter has to be a 2D tuple"
    cut_low, cut_high = params["wp"]
    assert (cut_low < cut_high), "The lower bound of the WP has to be smaller than the higher bound"
    mask = np.zeros(len(events), dtype='bool')
    mask = (events.FatJetGood[:,0][params["tagger"]] > cut_low) & (events.FatJetGood[:,0][params["tagger"]] <= cut_high)

    assert (params["category"] in ["pass", "fail"]), "The allowed categories for the tagger selection are 'pass' and 'fail'"
    if params["category"] == "fail":
        mask = ~mask & (events.FatJetGood[:,0][params["tagger"]] >= 0) & (events.FatJetGood[:,0][params["tagger"]] <= 1)

    return mask

def tagger_mask_inclusive_wp(events, params, **kwargs):
    if type(params["wp"]) == float:
        params["wp"] = (params["wp"], 1.0)
    assert (len(params["wp"]) == 2), "The 'wp' parameter has to be a 2D tuple"
    cut_low, cut_high = params["wp"]
    assert (cut_low < cut_high), "The lower bound of the WP has to be smaller than the higher bound"
    mask = (events.FatJetGood[params["tagger"]] > cut_low)

    assert (params["category"] in ["pass", "fail"]), "The allowed categories for the tagger selection are 'pass' and 'fail'"
    if params["category"] == "fail":
        mask = ~mask & (events.FatJetGood[params["tagger"]] >= 0) & (events.FatJetGood[params["tagger"]] <= 1)

    assert not ak.any(ak.is_none(mask)), f"None in tagger_mask_inclusive_wp, \n{events.nJetGood[ak.is_none(mask)]}"

    return mask

def get_tagger_pass(taggers, wp):
    return Cut(
        name=f"{'_'.join(taggers)}_pass",
        params={"taggers": taggers, "wp" : wp},
        function=tagger_pass
    )

def get_tagger_fail(taggers, wp):
    return Cut(
        name=f"{'_'.join(taggers)}_fail",
        params={"taggers": taggers, "wp" : wp},
        function=tagger_fail
    )

def get_tagger_passfail(taggers, wp, category):
    return Cut(
        name=f"{'_'.join(taggers)}_{category}",
        params={"taggers": taggers, "wp" : wp, "category": category},
        function=tagger_mask
    )

def get_exclusive_wp(tagger, wp, category):
    return Cut(
        name=f"{tagger}_{category}",
        params={"tagger": tagger, "wp" : wp, "category": category},
        function=tagger_mask_exclusive_wp
    )

def get_inclusive_wp(tagger, wp, category):
    return Cut(
        name=f"{tagger}_{category}",
        params={"tagger": tagger, "wp" : wp, "category": category},
        function=tagger_mask_inclusive_wp,
        collection="FatJetGood"
    )

def twojets_ptmsd(events, params, **kwargs):
    '''Mask to select events with at least one jet satisfying the pt, msd requirements
    and events with exactly two jets satisfying the pt, msd requirements.'''

    mask_one_jet = (
        ak.any(events.FatJetGood.pt > params["pt"], axis=1) &
        ak.any(events.FatJetGood.msoftdrop > params["msd"], axis=1)
    )

    mask_two_jets = (
        ak.all(events.FatJetGood.pt > params["pt"], axis=1) &
        ak.all(events.FatJetGood.msoftdrop > params["msd"], axis=1)
    )

    fatjet_mutag = (
        ( (events.nFatJetGood >= 1) & mask_one_jet ) |
        ( (events.nFatJetGood == 2) & mask_two_jets )
    )

    assert not ak.any(ak.is_none(fatjet_mutag)), f"None in mutag\n{fatjet_mutag}"

    return fatjet_mutag

def mutag_fatjet(events, params, **kwargs):
    # Select jets with a minimum number of matched muons
    mask_good_jets = (events.FatJetGood.nMuonGoodMatchedToFatJetGood >= params["nmu"])

    assert not ak.any(ak.is_none(mask_good_jets, axis=1)), f"None in mutag_fatjet"
    #mask_good_jets = mask_good_jets[~ak.is_none(mask, axis=1)]

    return mask_good_jets

def mutag_subjet(events, params, **kwargs):
    # Select jets with a minimum number of subjets
    mask_nsubjet = (ak.count(events.FatJetGood.subjets.pt, axis=2) >= params["nsubjet"])
    # Select jets with a minimum number of mu-tagged subjets
    if params["unique_matching"]:
        mask_nmusj = (events.FatJetGood.nMuonGoodMatchedUniquelyToSubJet >= params["nmuons"])
    else:
        mask_nmusj = (events.FatJetGood.nMuonGoodMatchedToSubJet >= params["nmuons"])

    mask_good_jets = mask_nsubjet & mask_nmusj
    assert not ak.any(ak.is_none(mask_good_jets, axis=1)), f"None in mutag_subjet"

    return mask_good_jets

def ptbin(events, params, **kwargs):
    # Mask to select events in a fatjet pt bin
    if params["pt_high"] == 'Inf':
        mask = (events.FatJetGood.pt > params["pt_low"])
    elif type(params["pt_high"]) != str:
        mask = (events.FatJetGood.pt > params["pt_low"]) & (events.FatJetGood.pt < params["pt_high"])
    else:
        raise NotImplementedError

    assert not ak.any(ak.is_none(mask, axis=1)), f"None in ptbin\n{events.nJetGood[ak.is_none(mask, axis=1)]}"

    return mask

def ptbin_mutag(events, params, **kwargs):
    return ptbin(events, params, **kwargs) & mutag(events, params, **kwargs)

def msoftdrop(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21
    #return (events.FatJetGood[:,0].pt > params["pt"]) & (events.FatJetGood[:,0].msoftdrop > params["msd"])
    mask = events.FatJetGood.msoftdrop > params["msd"]
    
    assert not ak.any(ak.is_none(mask), axis=1), f"None in ptmsd\n{events.FatJetGood.pt[ak.is_none(mask, axis=1)]}"

    return ak.where(~ak.is_none(mask, axis=1), mask, False)

def ptmsd(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21
    #return (events.FatJetGood[:,0].pt > params["pt"]) & (events.FatJetGood[:,0].msoftdrop > params["msd"])
    mask = (events.FatJetGood.pt > params["pt"]) & (events.FatJetGood.msoftdrop > params["msd"])

    assert not ak.any(ak.is_none(mask, axis=1)), f"None in ptmsd\n{events.FatJetGood.pt[ak.is_none(mask, axis=1)]}"

    return ak.where(~ak.is_none(mask, axis=1), mask, False)

def ptmsd_window(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum softdrop mass
    mask = (events.FatJetGood.pt > params["pt"]) & (events.FatJetGood.msoftdrop > params["msd_min"]) & (events.FatJetGood.msoftdrop < params["msd_max"])

    assert not ak.any(ak.is_none(mask, axis=1)), f"None in ptmsd_window\n{events.FatJetGood.pt[ak.is_none(mask, axis=1)]}"

    return ak.where(~ak.is_none(mask, axis=1), mask, False)


def ptmsdtau(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21
    mask = (events.FatJetGood.pt > params["pt"]) & (events.FatJetGood.msoftdrop > params["msd"]) & (events.FatJetGood.tau21 < params["tau21"])

    assert not ak.any(ak.is_none(mask, axis=1)), f"None in ptmsdtau\n{events.FatJetGood.pt[ak.is_none(mask, axis=1)]}"

    return ak.where(~ak.is_none(mask, axis=1), mask, False)

def ptmsdtauDDCvB(events, params, **kwargs):
    # Mask to select events with a fatjet with minimum softdrop mass and maximum tau21 and a requirement on the DDCvB score
    return (events.FatJetGood[:,0].pt > params["pt"]) & (events.FatJetGood[:,0].msoftdrop > params["msd"]) & (events.FatJetGood[:,0].tau21 < params["tau21"]) & (events.FatJetGood[:,0].btagDDCvBV2 > params["DDCvB"])

def min_nObj_minmsd(events, params, **kwargs):
    return ak.sum(events[params["coll"]].msoftdrop >= params["minmsd"], axis=1) >= params["N"]

##############################
## Factory method for HLT
def _get_trigger_mask_proxy(events, params, year, isMC, **kwargs):
    '''
    Helper function to call the HLT trigger mask
    '''
    return get_trigger_mask(events,
                            params["key"],
                            year,
                            isMC,
                            params["primaryDatasets"],
                            params["invert"])


def get_HLTsel(key, primaryDatasets=None, invert=False):
    '''Create the HLT trigger mask

    The Cut function reads the triggers configuration and create the mask.
    For MC the OR of all the triggers in the specific configuration key is performed.
    For DATA only the corresponding primary dataset triggers are applied.
    if primaryDatasets param is passed, the correspoding triggers are applied, both
    on DATA and MC, overwriting any other configuration.

    This is useful to remove the overlap of primary datasets in data. 

    :param key: Key in the trigger configuration for the list of triggers to apply
    :param primaryDatasets: (optional) list of primaryDatasets to use. Overwrites any other config
                                      both for Data and MC
    :param invert: invert the mask, if True the function returns events failing the HLT selection
 
    :returns: events mask
    '''
    name = f"HLT_{key}"
    if primaryDatasets:
        name += "_" + "_".join(primaryDatasets)
    if invert:
        name += "_NOT"
    return Cut(
        name = name,
        params = {"key": key,
                  "primaryDatasets": primaryDatasets,
                  "invert": invert},
        function = _get_trigger_mask_proxy 
    )

def flavor_mask(events, params, **kwargs):
    mask = {
        "l"  : events.FatJetGood.hadronFlavour < 4,
        "c"  : events.FatJetGood.hadronFlavour == 4,
        "b"  : events.FatJetGood.hadronFlavour == 5,
        "cc" : abs(events.FatJetGood.hadronFlavour == 4) & (events.FatJetGood.nBHadrons == 0) & (events.FatJetGood.nCHadrons >= 2),
        "bb" : abs(events.FatJetGood.hadronFlavour == 5) & (events.FatJetGood.nBHadrons >= 2)
    }

    if params["flavor"] in ["bb", "cc"]:
        return mask[params["flavor"]]
    elif params["flavor"] == "b":
        return mask[params["flavor"]] & ~mask["bb"]
    elif params["flavor"] == "c":
        return mask[params["flavor"]] & ~mask["cc"]
    elif params["flavor"] == "l":
        return mask[params["flavor"]] & ~mask["bb"] & ~mask["cc"] & ~mask["b"] & ~mask["c"]
    else:
        raise NotImplementedError
