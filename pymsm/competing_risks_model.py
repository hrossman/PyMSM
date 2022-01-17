# -- R source: https://github.com/JonathanSomer/covid-19-multi-state-model/blob/master/model/competing_risks_model.R --#

import numpy as np
import pandas as pd
from typing import List
from lifelines import CoxPHFitter


class CompetingRisksModel:
    def __init__(
        self, failure_types: List = None, event_specific_models: List = None
    ) -> None:
        """
        Each element of "event_specific_models"is a list
        with the following attributes:
        1. coefficients
        2. unique_event_times
        3. baseline_hazard
        4. cumulative_baseline_hazard_function
        """
        self.failure_types = failure_types
        self.event_specific_models = event_specific_models

    @staticmethod
    def _assert_valid_dataset(
        t: np.ndarray, failure_types: List, covariates_X: pd.DataFrame
    ):
        # t should be non-negative
        assert t >= 0

        # failure types should be integers from 0 to m, not necessarily consecutive
        assert all(isinstance(f, int) for f in failure_types)
        assert min(failure_types) >= 0

        # TODO
        # covariates should all be numerical
        # stopifnot(sapply(covariates_X, is.numeric))

        # all 3 arguments should have the same length of n
        assert len(t) == len(failure_types)
        assert len(covariates_X) == len(t)

    @staticmethod
    def _break_ties_by_adding_epsilon(
        t: np.ndarray, epsilon_min: float = 0.0, epsilon_max: float = 0.0001
    ):
        np.random.seed(42)
        eps = np.random.uniform(low=epsilon_min, high=epsilon_max, size=len(t))
        _, inverse, count = np.unique(
            t, return_inverse=True, return_counts=True, axis=0
        )
        non_unique_times_idx = np.where(count[inverse] > 1)[
            0
        ]  # find all indices where counts > 1
        t[((non_unique_times_idx) & (t != 0))] = (
            eps + t[((non_unique_times_idx) & (t != 0))]
        )
        return t

    @staticmethod
    def _fit_event_specific_model(
        t,
        failure_types,
        covariates_X: pd.DataFrame,
        type,
        sample_ids=None,
        t_start=None,
        sample_weights=None,
        verbose=1,
        **coxph_kwargs,
    ):
        # Treat all 'failure_types' except 'type' as censoring events
        is_event = failure_types == type

        if verbose >= 1:
            print(
                f">>> Fitting Transition to State: {type}, n events: {np.sum(is_event)}"
            )

        # TODO what is this:
        #     surv_object = if (is.null(t_start)) Surv(t, is_event) else Surv(t_start, t, is_event)

        cox_model = CoxPHFitter()
        cox_model.fit(
            df=covariates_X,
            duration_col="T",
            event_col="E",
            weights_col="sample_weights",
            cluster_col=None,
            **coxph_kwargs,
        )
        # TODO cluster col should be sample_ids?

        if verbose >= 2:
            cox_model.print_summary()

        return cox_model

    @staticmethod
    def _extract_necessary_attributes(cox_model):
        # TODO
        pass

    @staticmethod
    def _compute_cif_function(sample_covariates, failure_type):
        # TODO
        pass

    @staticmethod
    def _survival_function(time_passed, sample_covariates):
        # TODO
        pass

    def fit(
        self,
        t: np.ndarray,
        failure_types: np.ndarray,
        covariates_X: pd.DataFrame,
        sample_ids: List = None,
        t_start: float = None,
        break_ties: bool = True,
        sample_weights: np.ndarray = None,
        epsilon_min: float = 0.0,
        epsilon_max: float = 0.0001,
        verbose: int = 1,
    ):
        """
        Description:
        ------------------------------------------------------------------------------------------------------------
        This method fits a cox proportional hazards model for each failure type, treating others as censoring events.
        Tied event times are dealt with by adding an epsilon to tied event times.

        Arguments:
        ------------------------------------------------------------------------------------------------------------
        t : numeric vector
        A length n vector of positive times of events

        failure_types: numeric vector
        The event type corresponding to the time in vector t.
        Failure types are encoded as integers from 1 to m.
        Right-censoring events (the only kind of censoring supported) are encoded as 0.
        Thus, the failure type argument holds integers from 0 to m, where m is the number of distinct failure types

        covariates_X: numeric dataframe
        an n by #(covariates) numerical matrix
        All columns are used in the estimate.

        OPTIONAL:

        sample_ids:
        used inside the coxph model in order to identify subjects with repeating entries.

        t_start:
        A length n vector of positive start times, used in case of interval data.
        In that case: left=t_start, and right=t

        epsilon_min/max:
        epsilon is added to events with identical times to break ties.
        epsilon is sampled from a uniform distribution in the range (epsilon_min, epsilon_max)
        these values should be chosen so that they do not change the order of the events.
        """

        self._assert_valid_dataset(t, failure_types, covariates_X)

        if break_ties:
            t = self._break_ties_by_adding_epsilon(t, epsilon_min, epsilon_max)

        failure_types = np.unique(failure_types[failure_types > 0])
        for type in failure_types:
            cox_model = self._fit_event_specific_model(
                t,
                failure_types,
                covariates_X,
                type,
                sample_ids,
                t_start,
                sample_weights,
                verbose,
            )
            self.event_specific_models[type] = self._extract_necessary_attributes(
                cox_model
            )

    def predict_CIF(self, predict_at_t, sample_covariates, failure_type, time_passed=0):
        """
        Description:
        ------------------------------------------------------------------------------------------------------------
        This method computes the failure-type-specific cumulative incidence function, given that 'time_passed' time
        has passed (default is 0)
        
        Arguments:
        ------------------------------------------------------------------------------------------------------------
        predict_at_t: numeric vector
          times at which the cif will be computed
        
        sample_covariates: numeric vector
          a numerical vector of same length as the covariate matrix the model was fit to.
        
        failure_type: integer
          integer corresponing to the failure type, as given when fitting the model
        
        time_passed: numeric
          compute the cif conditioned on the fact that this amount of time has already passed.
        
        Returns:
        ------------------------------------------------------------------------------------------------------------
        the predicted cumulative incidence values for the given sample_covariates at times predict_at_t.
        """
        cif_function = self._compute_cif_function(sample_covariates, failure_type)

        predictions = cif_function(predict_at_t)

        # re-normalize the probability to account for the time passed
        if time_passed > 0:
            predictions = (
                predictions - cif_function(time_passed)
            ) / self.__annotations___survival_function(time_passed, sample_covariates)

        return predictions


if __name__ == "__main__":
    pass

