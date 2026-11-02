# Reference geometry behind the flanged-span cost scenarios

The [flanged system-cost packet](flanged-system-cost-study/README.md) compares
its fixed flanged composition against the mass-keyed cases in topology baseline
`55755de037fa3708aab0ff579caea20585c92e3da740505c395784aed6fe7d29`.
The baseline deliberately resizes prestress for each declared load case. Its
reference beam is therefore a different physical civil component in each row:

| Vehicle-mass case | Reference strands | Reference physical civil component |
|---|---:|---|
| Low | 25 | `ff3e6dda8b35eec0277334c271f58a3e579da77ce6bbec6ed19d036e0f6be21a` |
| Base | 26 | `fea2c6654db90339e5e32c7037349ed573722948ed759cb1f368bee7e31adfc7` |
| High | 27 | `065ee0924d6ba774db8157a9480814815226e0f463800cdc0060ef7bfac49a23` |

The published installed-cost deltas use the corresponding mass-specific
baseline case; they are not a sensitivity of one fixed reference beam. The
flanged geometry remains fixed within each of its own scenarios. Reference
foundation prices are unchanged proxies, and whole-life deltas remain held
because the separately modelled coating and bearing renewal scopes do not yet
match. None of these results establishes physical feasibility or selects a
railway design.
