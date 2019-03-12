import estimators.binary
import estimators.multi_class
import estimators.multi_label
import estimators.regression

model_by_name = {
  'binary': estimators.binary.models,
  'multi-class': estimators.multi_class.models,
  'multi-label': estimators.multi_label.models,
  'regression': estimators.regression.models,
}
