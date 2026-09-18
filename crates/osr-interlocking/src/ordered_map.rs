//! Sorted contiguous storage for the frequently updated derived-state tables.
//!
//! Lookup is logarithmic; insert/remove may move the suffix. Keys remain unique
//! and sorted, and serialization uses the same map representation as BTreeMap.
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::ops::Index;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OrderedMap<K, V> {
    entries: Vec<(K, Box<V>)>,
}

impl<K, V> Default for OrderedMap<K, V> {
    fn default() -> Self {
        Self {
            entries: Vec::new(),
        }
    }
}

impl<K: Ord, V> OrderedMap<K, V> {
    fn position(&self, key: &K) -> Result<usize, usize> {
        self.entries
            .binary_search_by(|(candidate, _)| candidate.cmp(key))
    }
    pub fn get(&self, key: &K) -> Option<&V> {
        self.position(key)
            .ok()
            .map(|index| self.entries[index].1.as_ref())
    }
    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        match self.position(&key) {
            Ok(index) => Some(std::mem::replace(self.entries[index].1.as_mut(), value)),
            Err(index) => {
                self.entries.insert(index, (key, Box::new(value)));
                None
            }
        }
    }
    pub fn get_or_insert_with(&mut self, key: K, value: impl FnOnce() -> V) -> &mut V {
        let index = match self.position(&key) {
            Ok(index) => index,
            Err(index) => {
                self.entries.insert(index, (key, Box::new(value())));
                index
            }
        };
        self.entries[index].1.as_mut()
    }
    pub fn remove(&mut self, key: &K) -> Option<V> {
        self.position(key)
            .ok()
            .map(|index| *self.entries.remove(index).1)
    }
    pub fn retain(&mut self, mut keep: impl FnMut(&K, &mut V) -> bool) {
        let mut index = 0;
        while index < self.entries.len() {
            let (key, value) = &mut self.entries[index];
            if keep(key, value) {
                index += 1;
            } else {
                self.entries.remove(index);
            }
        }
    }
    pub fn len(&self) -> usize {
        self.entries.len()
    }
    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
    pub fn values(&self) -> impl Iterator<Item = &V> {
        self.entries.iter().map(|(_, value)| value.as_ref())
    }
    pub fn iter(&self) -> impl Iterator<Item = (&K, &V)> {
        self.entries
            .iter()
            .map(|(key, value)| (key, value.as_ref()))
    }
}

impl<K: Ord, V> Index<&K> for OrderedMap<K, V> {
    type Output = V;
    fn index(&self, key: &K) -> &V {
        self.get(key).expect("no entry found for key")
    }
}

impl<K: Ord + Serialize, V: Serialize> Serialize for OrderedMap<K, V> {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.collect_map(self.iter())
    }
}

impl<'de, K: Ord + Deserialize<'de>, V: Deserialize<'de>> Deserialize<'de> for OrderedMap<K, V> {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        // Preserve the existing serde map semantics, including duplicate keys.
        let map = std::collections::BTreeMap::<K, V>::deserialize(deserializer)?;
        Ok(Self {
            entries: map
                .into_iter()
                .map(|(key, value)| (key, Box::new(value)))
                .collect(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;
    use std::collections::BTreeMap;

    proptest! {
        #[test]
        fn operations_match_btree(ops in prop::collection::vec((0_u8..5, any::<u8>(), any::<i32>()), 0..200)) {
            let mut actual = OrderedMap::default();
            let mut expected = BTreeMap::new();
            for (op, key, value) in ops {
                match op {
                    0 => prop_assert_eq!(actual.insert(key, value), expected.insert(key, value)),
                    1 => prop_assert_eq!(actual.remove(&key), expected.remove(&key)),
                    2 => {
                        let a = actual.get_or_insert_with(key, || value);
                        let b = expected.entry(key).or_insert_with(|| value);
                        *a = a.wrapping_add(1);
                        *b = b.wrapping_add(1);
                        prop_assert_eq!(*a, *b);
                    }
                    3 => {
                        let keep = |k: &u8, v: &mut i32| { *v = v.wrapping_add(value); *k >= key };
                        actual.retain(keep);
                        expected.retain(keep);
                    }
                    _ => prop_assert_eq!(actual.get(&key), expected.get(&key)),
                }
                prop_assert_eq!(actual.len(), expected.len());
                prop_assert_eq!(actual.is_empty(), expected.is_empty());
                prop_assert_eq!(actual.iter().collect::<Vec<_>>(), expected.iter().collect::<Vec<_>>());
                prop_assert_eq!(actual.values().collect::<Vec<_>>(), expected.values().collect::<Vec<_>>());
                let json = serde_json::to_string(&actual).unwrap();
                prop_assert_eq!(&json, &serde_json::to_string(&expected).unwrap());
                let restored: OrderedMap<u8, i32> = serde_json::from_str(&json).unwrap();
                prop_assert_eq!(&restored, &actual);
            }
        }
    }

    #[test]
    fn duplicate_keys_and_lazy_initialization_match_existing_map() {
        let mut map: OrderedMap<u8, i32> = serde_json::from_str(r#"{"2":1,"1":3,"2":4}"#).unwrap();
        assert_eq!(serde_json::to_string(&map).unwrap(), r#"{"1":3,"2":4}"#);
        assert_eq!(
            *map.get_or_insert_with(2, || panic!("existing value must be kept")),
            4
        );
        assert_eq!(map[&1], 3);
    }
}
